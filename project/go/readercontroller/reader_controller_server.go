package readercontroller

import (
	"context"
	"go-root/lib/errs"
	"go-root/lib/log"
	"go-root/proto_impl/reader_controller"
	emptypb "google.golang.org/protobuf/types/known/emptypb"
)

type GRPCServer struct {
	reader_controller.UnimplementedReaderControllerServiceServer
	Logger     log.Logger
	Controller ReaderController
}

func (r *GRPCServer) CreateClient(ctx context.Context, c2 *reader_controller.CreateClientRequest) (*reader_controller.CreateClientResponse, error) {
	sessionID, err := r.Controller.CreateClient(ctx, c2.GetApiId(), c2.GetApiHash(), c2.GetUserId())
	if err != nil {
		return nil, errs.New(err)
	}
	return &reader_controller.CreateClientResponse{SessionId: sessionID}, nil
}

func (r *GRPCServer) LoadClient(ctx context.Context, req *reader_controller.LoadClientRequest) (*emptypb.Empty, error) {
	if err := r.Controller.LoadClient(ctx, req.GetSessionId(), req.GetUserId()); err != nil {
		return nil, errs.New(err)
	}
	return &emptypb.Empty{}, nil
}

func (r *GRPCServer) UnLoadClient(ctx context.Context, req *reader_controller.UnLoadClientRequest) (*emptypb.Empty, error) {
	if err := r.Controller.UnLoadClient(ctx, req.GetSessionId(), req.GetUserId()); err != nil {
		return nil, errs.New(err)
	}
	return &emptypb.Empty{}, nil
}

func (r *GRPCServer) SignInClient(ctx context.Context, req *reader_controller.SignInClientRequest) (*reader_controller.SignInClientResponse, error) {
	status, phoneCodeHash, err := r.Controller.SignInClient(ctx, req.GetSessionId(), req.GetPhone(), req.GetUserId())
	if err != nil {
		return nil, errs.New(err)
	}

	var protoStatus reader_controller.SignInClientResponse_Status
	switch status {
	case SignInNeedCode:
		protoStatus = reader_controller.SignInClientResponse_NEED_CODE
	case SignInSuccess:
		protoStatus = reader_controller.SignInClientResponse_SUCCESS
	default:
		return nil, errs.New("unknown status: %d", int(status))
	}

	return &reader_controller.SignInClientResponse{
		Status:        protoStatus,
		PhoneCodeHash: phoneCodeHash,
	}, nil
}

func (r *GRPCServer) CompleteSignInClient(ctx context.Context, req *reader_controller.CompleteSignInRequest) (*emptypb.Empty, error) {
	if err := r.Controller.CompleteSignInClient(
		ctx,
		req.GetSessionId(),
		req.GetPhone(),
		req.GetCode(),
		req.GetPhoneCodeHash(),
		req.GetPassword(),
		req.GetUserId(),
	); err != nil {
		return nil, errs.New(err)
	}
	return &emptypb.Empty{}, nil
}

func (r *GRPCServer) ListClients(ctx context.Context, req *reader_controller.ListClientsRequest) (*reader_controller.ListClientsResponse, error) {
	sessionIDs, err := r.Controller.ListClients(ctx, req.GetUserId())
	if err != nil {
		return nil, errs.New(err)
	}
	return &reader_controller.ListClientsResponse{SessionIds: sessionIDs}, nil
}

func (r *GRPCServer) GetDialogs(ctx context.Context, req *reader_controller.GetDialogsRequest) (*reader_controller.GetDialogsResponse, error) {
	dialogs, err := r.Controller.GetDialogs(ctx, req.GetSessionId(), req.GetUserId())
	if err != nil {
		return nil, errs.New(err)
	}

	pbDialogs := make([]*reader_controller.Dialog, len(dialogs))
	for i, d := range dialogs {
		pbDialogs[i] = &reader_controller.Dialog{
			Id:    d.ID,
			Title: d.Title,
		}
	}

	return &reader_controller.GetDialogsResponse{Dialogs: pbDialogs}, nil
}

func (r *GRPCServer) StartReadMessage(ctx context.Context, req *reader_controller.StartReadMessageRequest) (*emptypb.Empty, error) {
	if err := r.Controller.StartReadMessage(ctx, req.GetSessionId(), req.GetUserId()); err != nil {
		return nil, errs.New(err)
	}
	return &emptypb.Empty{}, nil
}
