package readercontroller

import (
	"container/heap"
	"sync"
)

// telegramReaderServiceClientHeap 定義一個整數切片，實作 heap.Interface
// 用來取得最少 session count 的 client
type telegramReaderServiceClientHeap struct {
	slice []*myTelegramReaderServiceClientWithReferenceCount
	lock  sync.Mutex
	index map[*myTelegramReaderServiceClientWithReferenceCount]int
}

// 以下四個方法構成 heap.Interface 的必要實作

func (h *telegramReaderServiceClientHeap) Len() int { return len(h.slice) }
func (h *telegramReaderServiceClientHeap) Less(i, j int) bool {
	h.lock.Lock()
	defer h.lock.Unlock()
	return h.slice[i].referenceCount.Load() < h.slice[j].referenceCount.Load()
} // 小頂堆：h[i] < h[j]
// 如果想要大頂堆，改為 h[i] > h[j]

func (h *telegramReaderServiceClientHeap) Swap(i, j int) {
	h.lock.Lock()
	defer h.lock.Unlock()
	h.slice[i], h.slice[j] = h.slice[j], h.slice[i]
	// 同步更新映射
	h.index[h.slice[i]] = i
	h.index[h.slice[j]] = j
}

// Push 和 Pop 使用指標接收者，以便修改底層切片
func (h *telegramReaderServiceClientHeap) Push(x interface{}) {
	h.lock.Lock()
	defer h.lock.Unlock()
	h.slice = append(h.slice, x.(*myTelegramReaderServiceClientWithReferenceCount))
	h.index[x.(*myTelegramReaderServiceClientWithReferenceCount)] = len(h.slice) - 1
}

func (h *telegramReaderServiceClientHeap) Pop() interface{} {
	h.lock.Lock()
	defer h.lock.Unlock()
	old := h.slice
	n := len(old)
	x := old[n-1]
	h.slice = old[:n-1]
	delete(h.index, x)
	return x
}

func (h *telegramReaderServiceClientHeap) Remove(v *myTelegramReaderServiceClientWithReferenceCount) bool {
	h.lock.Lock()
	defer h.lock.Unlock()

	i, ok := h.index[v]
	if !ok {
		return false
	}
	heap.Remove(h, i)
	return true
}

func (h *telegramReaderServiceClientHeap) Load(i int) (*myTelegramReaderServiceClientWithReferenceCount, bool) {
	if len(h.slice) <= i {
		return nil, false
	}
	return h.slice[i], true
}

func NewTelegramReaderServiceClientHeap() *telegramReaderServiceClientHeap {
	return &telegramReaderServiceClientHeap{
		index: make(map[*myTelegramReaderServiceClientWithReferenceCount]int),
	}
}
