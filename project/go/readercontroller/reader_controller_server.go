package readercontroller

import (
	"go-root/lib/log"
	"go-root/proto_impl/reader_controller"
)

type ReaderControllerServer struct {
	reader_controller.UnimplementedReaderControllerServiceServer
	logger log.Logger
}
