from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Type, Any, TypeVar


class AbstractLinkedNode(ABC):
    def __init__(self, value: Any):
        self.value = value


class AbstractSinglyLinkedNode(AbstractLinkedNode, ABC):
    def __init__(
            self,
            value: Any,
            next_node: Optional[Type[AbstractLinkedNode]] = None
    ):
        super().__init__(value)
        self.next = next_node


class AbstractDoublyLinkedNode(AbstractSinglyLinkedNode, ABC):
    def __init__(
            self,
            value: Any,
            next_node: Optional[Type[AbstractLinkedNode]] = None,
            prev_node: Optional[Type[AbstractLinkedNode]] = None
    ):
        super().__init__(value, next_node)
        self.prev = prev_node


NodeType = TypeVar('NodeType', AbstractSinglyLinkedNode, AbstractDoublyLinkedNode)


class AbstractLinkedList(ABC):
    def __init__(self, head: Optional[NodeType] = None):
        self._head = head

    @property
    def first(self):
        return self._head

    @property
    @abstractmethod
    def last(self):
        pass

    @abstractmethod
    def add(self, node: NodeType):
        self.last.next = node

    @abstractmethod
    def pop_first(self):
        pass

    @abstractmethod
    def pop_last(self):
        pass


class AbstractLinearLinkedList(AbstractLinkedList, ABC):
    @property
    def last(self):
        curr = self._head
        while curr.next:
            curr = curr.next
        return curr

    def add(self, node: NodeType):
        self.last.next = node

    def pop_first(self):
        to_pop = self._head
        self._head = self._head.next
        return to_pop

    def pop_last(self):
        curr = self._head
        if curr is None:
            return

        while curr.next and curr.next.next:
            curr = curr.next

        to_pop = curr.next
        curr.next = None
        return to_pop


class AbstractCircularLinkedList(AbstractLinkedList, ABC):
    pass
