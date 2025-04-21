package readercontroller

import (
	"context"
	"github.com/google/uuid"
	"go-root/lib/errs"
	"go-root/proto_impl/telegram_reader"
	"go-root/readercontroller/dal"
)

type Dialog struct {
	ID    int64
	Title string
}
type SignInStatus int

const (
	SignInNeedCode SignInStatus = iota
	SignInSuccess
)

type ReaderController interface {
	CreateClient(ctx context.Context, apiID int32, apiHash string, userID string) (sessionID string, err error)
	LoadClient(ctx context.Context, sessionID string, userID string) error
	UnLoadClient(ctx context.Context, sessionID string, userID string) error
	SignInClient(ctx context.Context, sessionID string, phone string, userID string) (status SignInStatus, phoneCodeHash string, err error)
	CompleteSignInClient(ctx context.Context, sessionID, phone, code, phoneCodeHash, password, userID string) error
	ListClients(ctx context.Context, userID string) (sessionIDs []string, err error)
	GetDialogs(ctx context.Context, sessionID string, userID string) (dialogs []Dialog, err error)
	StartReadMessage(ctx context.Context, sessionID string, userID string) error
}

type readerController struct {
	db      dal.DAL
	manager ClientManager
}

func (r *readerController) checkIfSessionExist(ctx context.Context, sessionID string, userID string) (bool, error) {
	exist, err := r.db.CheckIfSessionExist(ctx, sessionID, userID)
	if err != nil {
		return false, errs.New(err)
	}
	return exist, nil

}
func (r *readerController) CreateClient(ctx context.Context, apiID int32, apiHash string, userID string) (sessionID string, err error) {
	client, err := r.manager.FindAvailableClient(ctx)
	if err != nil {
		return "", errs.New(err)
	}
	resp, err := client.CreateClient(ctx, &telegram_reader.CreateClientRequest{
		ApiId:   apiID,
		ApiHash: apiHash,
	})
	if err != nil {
		return "", errs.New(err)
	}
	sessionID = resp.GetSessionId()
	sessionIDUUID, err := uuid.Parse(sessionID)
	if err != nil {
		return "", errs.New(err)
	}

	err = r.db.CreateTelegramClient(ctx, dal.TelegramClient{
		UserID:    userID,
		SessionID: sessionIDUUID,
	})
	if err != nil {
		return "", errs.New(err)
	}

	return sessionID, nil
}

func (r *readerController) LoadClient(ctx context.Context, sessionID string, userID string) error {
	exist, err := r.checkIfSessionExist(ctx, sessionID, userID)
	if err != nil {
		return errs.New(err)
	}
	if !exist {
		return errs.New("session ID for user: %s, session ID: %s not found", userID, sessionID)
	}
	client, exist, err := r.manager.FindClientBySessionID(ctx, sessionID)
	if err != nil {
		return errs.New(err)
	}
	if exist {
		return errs.New("client for session ID: %s already loaded, running on %s", sessionID, client.GetName())
	}

	availableClient, err := r.manager.FindAvailableClient(ctx)
	_, err = availableClient.LoadClient(ctx, &telegram_reader.LoadClientRequest{
		SessionId: sessionID,
	})
	if err != nil {
		return errs.New(err)
	}
	return nil
}

func (r *readerController) UnLoadClient(ctx context.Context, sessionID string, userID string) error {
	exist, err := r.checkIfSessionExist(ctx, sessionID, userID)
	if err != nil {
		return errs.New(err)
	}
	if !exist {
		return errs.New("session ID for user: %s, session ID: %s not found", userID, sessionID)
	}

	client, exist, err := r.manager.FindClientBySessionID(ctx, sessionID)
	if err != nil {
		return errs.New(err)
	}
	if !exist {
		return errs.New("client for session ID: %s is not loaded", sessionID)
	}

	_, err = client.UnLoadClient(ctx, &telegram_reader.UnLoadClientRequest{
		SessionId: sessionID,
	})
	if err != nil {
		return errs.New(err)
	}
	return nil
}

func (r *readerController) SignInClient(ctx context.Context, sessionID string, phone string, userID string) (status SignInStatus, phoneCodeHash string, err error) {
	exist, err := r.checkIfSessionExist(ctx, sessionID, userID)
	if err != nil {
		return 0, "", errs.New(err)
	}
	if !exist {
		return 0, "", errs.New("session ID for user: %s, session ID: %s not found", userID, sessionID)
	}
	client, exist, err := r.manager.FindClientBySessionID(ctx, sessionID)
	if err != nil {
		return 0, "", errs.New(err)
	}
	if !exist {
		return 0, "", errs.New("client for session ID: %s is not loaded", sessionID)
	}
	resp, err := client.SignInClient(ctx, &telegram_reader.SignInClientRequest{
		SessionId: sessionID,
		Phone:     phone,
	})
	if err != nil {
		return 0, "", errs.New(err)
	}
	switch resp.GetStatus() {
	case telegram_reader.SignInClientResponse_SUCCESS:
		status = SignInSuccess
	case telegram_reader.SignInClientResponse_NEED_CODE:
		status = SignInNeedCode
	default:
		return 0, "", errs.New("unknown sign in status: %s", resp.GetStatus())
	}
	return status, resp.GetPhoneCodeHash(), nil
}

func (r *readerController) CompleteSignInClient(ctx context.Context, sessionID, phone, code, phoneCodeHash, password, userID string) error {
	exist, err := r.checkIfSessionExist(ctx, sessionID, userID)
	if err != nil {
		return errs.New(err)
	}
	if !exist {
		return errs.New("session ID for user: %s, session ID: %s not found", userID, sessionID)
	}
	client, exist, err := r.manager.FindClientBySessionID(ctx, sessionID)
	if err != nil {
		return errs.New(err)
	}
	if !exist {
		return errs.New("client for session ID: %s is not loaded", sessionID)
	}
	_, err = client.CompleteSignInClient(ctx, &telegram_reader.CompleteSignInRequest{
		SessionId:     sessionID,
		Phone:         phone,
		Code:          code,
		PhoneCodeHash: phoneCodeHash,
		Password:      password,
	})
	if err != nil {
		return errs.New(err)
	}
	return nil
}

func (r *readerController) ListClients(ctx context.Context, userID string) (sessionIDs []string, err error) {
	sessions, err := r.db.GetSessionIDsByUserName(ctx, userID)
	if err != nil {
		return nil, errs.New(err)
	}

	// iterate over the sessions and convert them to string
	sessionIDs = make([]string, len(sessions))
	for i, session := range sessions {
		sessionIDs[i] = session.String()
	}

	return sessionIDs, nil
}

func (r *readerController) GetDialogs(ctx context.Context, sessionID string, userID string) (dialogs []Dialog, err error) {
	exist, err := r.checkIfSessionExist(ctx, sessionID, userID)
	if err != nil {
		return nil, errs.New(err)
	}
	if !exist {
		return nil, errs.New("session ID for user: %s, session ID: %s not found", userID, sessionID)
	}
	client, exist, err := r.manager.FindClientBySessionID(ctx, sessionID)
	if err != nil {
		return nil, errs.New(err)
	}
	if !exist {
		return nil, errs.New("client for session ID: %s is not loaded", sessionID)
	}
	resp, err := client.GetDialogs(ctx, &telegram_reader.GetDialogsRequest{
		SessionId: sessionID,
	})
	if err != nil {
		return nil, errs.New(err)
	}
	dialogs = make([]Dialog, len(resp.GetDialogs()))
	for i, dialog := range resp.GetDialogs() {
		dialogs[i] = Dialog{
			ID:    dialog.GetId(),
			Title: dialog.GetTitle(),
		}
	}
	return dialogs, nil
}

func (r *readerController) StartReadMessage(ctx context.Context, sessionID string, userID string) error {
	exist, err := r.checkIfSessionExist(ctx, sessionID, userID)
	if err != nil {
		return errs.New(err)
	}
	if !exist {
		return errs.New("session ID for user: %s, session ID: %s not found", userID, sessionID)
	}
	client, exist, err := r.manager.FindClientBySessionID(ctx, sessionID)
	if err != nil {
		return errs.New(err)
	}
	if !exist {
		return errs.New("client for session ID: %s is not loaded", sessionID)
	}
	_, err = client.StartReadMessage(ctx, &telegram_reader.StartReadMessageRequest{
		SessionId: sessionID,
	})
	if err != nil {
		return errs.New(err)
	}
	return nil
}

func NewReaderController(db dal.DAL, manager ClientManager) ReaderController {
	return &readerController{db: db, manager: manager}
}
