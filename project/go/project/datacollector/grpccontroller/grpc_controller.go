package grpccontroller

import (
	"core/grpc"
	pb "proto"
)

// server 實作了 pb.UnimplementedCollectorServiceServer 接口
type server struct {
	pb.UnimplementedCollectorServiceServer
}

func MountRoutes(s grpc.GrpcEngine) {
	sv := &server{}
	pb.RegisterCollectorServiceServer(s, sv)
}
