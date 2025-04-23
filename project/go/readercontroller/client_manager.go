package readercontroller

import (
	"context"
	"fmt"
	"go-root/config"
	"go-root/lib/errs"
	"go-root/lib/log"
	"go-root/readercontroller/dal"
	"go-root/readercontroller/telegramreader"
	"strings"
	"sync"
	"time"
)

type clientManager struct {
	dal                               dal.DAL
	logger                            log.Logger
	sessionIDToClientMap              sync.Map // map[sessionID]MyTelegramReaderServiceClientWithReferenceCount
	hostNameToSessionID               sync.Map //map[string]map[string]struct{}
	serviceClientWithSessionCountHeap telegramreader.TelegramReaderServiceClientHeap
	onClose                           []func(ctx context.Context) error
}

func (c *clientManager) Close(ctx context.Context) error {
	c.logger.Debugf("clientManager.Close: running %d onClose callbacks", len(c.onClose))
	var err error
	for i := len(c.onClose) - 1; i >= 0; i-- {
		f := c.onClose[i]
		e := f(ctx)
		if e != nil {
			if err == nil {
				err = e
			} else {
				err = fmt.Errorf("%v; %w", err, e)
			}
		}
	}

	c.hostNameToSessionID.Range(func(hostName, _ interface{}) bool {
		c.removeHostName(hostName.(string))
		return true
	})
	return err
}

func (c *clientManager) FindAvailableClient(ctx context.Context) (telegramreader.MyTelegramReaderServiceClient, error) {
	c.logger.Debugf("FindAvailableClient called")
	client, ok := c.serviceClientWithSessionCountHeap.Load(0)
	if !ok {
		return nil, fmt.Errorf("no available client")
	}
	return client, nil
}

func (c *clientManager) parseHostNameFromKey(key string) (string, error) {
	parts := strings.Split(key, ":")
	if len(parts) != 2 {
		return "", fmt.Errorf("invalid key format: %s", key)
	}
	return parts[1], nil
}

// this should be called only once when the object is created
func (c *clientManager) syncReaders(ctx context.Context) error {
	onNew, onDelete, onError, closeFunc := c.dal.SubscribeTelegramReaderChange(ctx)
	c.onCloseCallback(func(ctx context.Context) error {
		err := closeFunc()
		if err != nil {
			return errs.New("error when close SubscribeTelegramReader: %s", err.Error())
		}
		return nil
	})

	c.logger.Debugf("syncReaders: subscribed to reader changes")

	go func() {
		for {
			select {
			case newClientHostNames, ok := <-onNew:
				if !ok {
					return
				}
				timeoutCtx, cancel := context.WithTimeout(ctx, time.Second*5)
				for _, keyName := range newClientHostNames {
					hostName, e := c.parseHostNameFromKey(keyName)
					if e != nil {
						c.logger.Errorf("parseHostNameFromKey error: %v", errs.New(e))
					}
					e = c.loadClientByHostName(timeoutCtx, hostName)
					if e != nil {
						c.logger.Errorf("loadClientByHostName error: %v", errs.New(e))
					}
				}
				cancel()
			case deletedClientHostNames, ok := <-onDelete:
				if !ok {
					return
				}
				timeoutCtx, cancel := context.WithTimeout(ctx, time.Second*5)
				for _, keyName := range deletedClientHostNames {
					hostName, e := c.parseHostNameFromKey(keyName)
					if e != nil {
						c.logger.Errorf("parseHostNameFromKey error: %v", errs.New(e))
					}
					e = c.removeClientByHostName(timeoutCtx, hostName)
					if e != nil {
						c.logger.Errorf("loadClientByHostName error: %v", errs.New(e))
					}
				}
				cancel()
			case err, ok := <-onError:
				if !ok {
					return
				}
				c.logger.Errorf("error when reading SubscribeTelegramReaderChange: %v", errs.New(err))
			}
		}
	}()

	return nil
}

func (c *clientManager) FindClientBySessionID(ctx context.Context, sessionID string) (telegramreader.MyTelegramReaderServiceClient, bool, error) {
	c.logger.Debugf("FindClientBySessionID: looking up sessionID %s", sessionID)
	cli, exist := c.sessionIDToClientMap.Load(sessionID)
	if !exist {
		return nil, false, nil
	}
	client := cli.(telegramreader.MyTelegramReaderServiceClientWithReferenceCount)
	return client, true, nil
}

func (c *clientManager) onCloseCallback(f func(ctx context.Context) error) {
	c.onClose = append(c.onClose, f)
}

func (c *clientManager) getTelegramReaderURL(hostName string) string {
	headlessURL := config.GetConfig().TelegramReader.HeadlessURL
	addr := fmt.Sprintf("%s.%s", hostName, headlessURL)
	return addr
}

func (c *clientManager) loadClientByHostName(ctx context.Context, hostName string) error {
	c.logger.Infof("loadClientByHostName: resolving URL for hostName %s", hostName)
	addr := c.getTelegramReaderURL(hostName)

	client, err := telegramreader.NewMyTelegramReaderServiceClient(addr, hostName)
	if err != nil {
		return errs.New(err)
	}

	clientWithReferenceCount := telegramreader.NewMyTelegramReaderServiceClientWithReferenceCount(
		client,
		c.serviceClientWithSessionCountHeap,
		c.logger,
	)
	c.logger.Debugf("loadClientByHostName: created clientWithReferenceCount for hostName %s", hostName)

	err = c.syncReaderSessions(ctx, hostName, clientWithReferenceCount)
	if err != nil {
		return errs.New(err)
	}
	return nil
}

func (c *clientManager) syncReaderSessions(ctx context.Context, hostName string, client telegramreader.MyTelegramReaderServiceClientWithReferenceCount) error {
	c.logger.Debugf("syncReaderSessions: subscribed to session changes for hostName %s", hostName)
	onNew, onDelete, onError, closeFunc := c.dal.SubscribeTelegramReaderSessionChange(ctx, hostName)
	client.AddOnClose(func(ctx context.Context) error {
		err := closeFunc()
		if err != nil {
			return errs.New(err)
		}
		return nil
	})

	go func() {
		for {
			select {
			case newSessionIDs, ok := <-onNew:
				if !ok {
					return
				}
				for _, sessionID := range newSessionIDs {
					c.storeSessionIDToClient(hostName, sessionID, client)
				}

			case deletedSessionIDs, ok := <-onDelete:
				if !ok {
					return
				}
				for _, sessionID := range deletedSessionIDs {
					c.removeSessionIDToClient(hostName, sessionID)
				}
			case err, ok := <-onError:
				if !ok {
					return
				}
				c.logger.Errorf("error when reading SubscribeTelegramReaderSessionChange: %v", errs.New(err))
			}
		}
	}()
	return nil
}

func (c *clientManager) storeSessionIDToClient(hostName string, sessionID string, client telegramreader.MyTelegramReaderServiceClientWithReferenceCount) {
	c.logger.Infof("storeSessionIDToClient: storing sessionID %s for hostName %s", sessionID, hostName)
	c.appendHostNameToSessionID(hostName, sessionID)
	oldClient, loaded := c.sessionIDToClientMap.LoadOrStore(sessionID, client)
	client.AddSessionCount()
	if loaded {
		c.logger.Errorf("sessionID %s already exists, replacing with new client", sessionID)
		theOldClient := oldClient.(telegramreader.MyTelegramReaderServiceClientWithReferenceCount)
		theOldClient.DeductSessionCount()
	}
}

func (c *clientManager) removeSessionIDToClient(hostName string, sessionID string) {
	c.logger.Infof("removeSessionIDToClient: removing sessionID %s for hostName %s", sessionID, hostName)
	oldClient, loaded := c.sessionIDToClientMap.LoadAndDelete(sessionID)
	if loaded {
		theOldClient := oldClient.(telegramreader.MyTelegramReaderServiceClientWithReferenceCount)
		remainReferenceCount := theOldClient.DeductSessionCount()
		if remainReferenceCount == 0 {
			c.removeHostName(hostName)
		} else {
			c.removeHostNameToSessionID(hostName, sessionID)
		}
		return
	}
	c.logger.Errorf("tring to remove sessionID %s, but not found in sessionIDToClientMap", sessionID)
}

func (c *clientManager) appendHostNameToSessionID(hostName string, sessionID string) {
	c.logger.Debugf("appendHostNameToSessionID: hostName=%s, sessionID=%s", hostName, sessionID)
	sessionIDMap := sync.Map{}
	sessionIDMap.Store(sessionID, struct{}{})
	existIDMap, loaded := c.hostNameToSessionID.LoadOrStore(hostName, &sessionIDMap)
	if loaded {
		// 如果已經存在，則將新的 sessionID 添加到現有的映射中
		existIDMap.(*sync.Map).Store(sessionID, struct{}{})
		return
	}
}

func (c *clientManager) removeHostNameToSessionID(hostName string, sessionID string) {
	c.logger.Infof("removeHostNameToSessionID: hostName=%s, sessionID=%s", hostName, sessionID)
	existIDMap, loaded := c.hostNameToSessionID.Load(hostName)
	if loaded {
		existIDMap.(*sync.Map).Delete(sessionID)
		return
	}
	c.logger.Errorf("hostName %s not found in hostNameToSessionID map", hostName)
}

func (c *clientManager) removeHostName(hostName string) {
	c.logger.Infof("removeHostName: removing hostName %s", hostName)
	sessionMap, loaded := c.hostNameToSessionID.LoadAndDelete(hostName)
	if !loaded {
		c.logger.Errorf("hostName %s not found in hostNameToSessionID map", hostName)
		return
	}
	sessionCount := 0
	sessionMap.(*sync.Map).Range(func(key, value interface{}) bool {
		sessionCount++
		return true
	})
	if sessionCount != 1 {
		c.logger.Errorf("sessionCount %d != 1, hostName %s", sessionCount, hostName)
	}
}

func (c *clientManager) removeClientByHostName(_ context.Context, hostName string) error {
	c.logger.Infof("removeClientByHostName: removing all sessions for hostName %s", hostName)
	sessionIDs, loaded := c.hostNameToSessionID.Load(hostName)
	if !loaded {
		return nil
	}
	sessionIDs.(*sync.Map).Range(func(key, _ interface{}) bool {
		sessionID := key.(string)
		// will automatically remove hostName from c.hostNameToSessionID when last sessionID removed
		c.removeSessionIDToClient(hostName, sessionID)
		return true
	})
	return nil
}

type ClientManager interface {
	FindAvailableClient(ctx context.Context) (telegramreader.MyTelegramReaderServiceClient, error)
	FindClientBySessionID(ctx context.Context, sessionID string) (telegramreader.MyTelegramReaderServiceClient, bool, error)
	Close(ctx context.Context) error
}

func NewClientManager(ctx context.Context, logger log.Logger, dataAccessLayer dal.DAL) (ClientManager, error) {
	manager := &clientManager{
		dal:                               dataAccessLayer,
		logger:                            logger,
		serviceClientWithSessionCountHeap: telegramreader.NewTelegramReaderServiceClientHeap(),
	}
	err := manager.syncReaders(ctx)
	if err != nil {
		return nil, errs.New(err)
	}
	return manager, nil
}
