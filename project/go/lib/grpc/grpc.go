package grpc

import (
	"context"
	"go-root/lib/errs"
	"google.golang.org/grpc"
	"net"
)

type GrpcEngine interface {
	grpc.ServiceRegistrar
	Start(addr string) error
	Stop(ctx context.Context) error
}

type grpcEngine struct {
	*grpc.Server
}

func (g *grpcEngine) Start(addr string) error {
	lis, err := net.Listen("tcp", addr)
	if err != nil {
		return errs.New("failed to listen: %v", err)
	}
	if e := g.Server.Serve(lis); e != nil {
		return errs.New("failed to serve: %v", e)
	}
	return nil
}

func (g *grpcEngine) Stop(ctx context.Context) error {
	g.Server.GracefulStop()
	return nil
}

func NewGrpcEngine() GrpcEngine {
	s := grpc.NewServer()
	return &grpcEngine{
		Server: s,
	}
}
