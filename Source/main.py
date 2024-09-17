import argparse
import bisect
import csv
import os
import pickle
import sys
from enum import Enum
from math import ceil

sys.setrecursionlimit(100000)


degree = 0
bptree = None


class DeleteStatus(Enum):
    OK = 0
    UNDERFLOW = 1
    MERGE = 2


def leaf(node):
    return len(node.children) == 0


def internal(node):
    return len(node.children) > 0


def full(node, MAX_KEYS):
    return len(node.keys) == MAX_KEYS


class BPTree:
    def __init__(self, degree):
        self.root = Node(degree)
        self.degree = degree

    def insert(self, key, value):
        result = self.root.insert(key, value)

        # 루트 노드에서 분할이 일어났을 때 처리
        if result:
            split_key, new_node = result
            new_root = Node(self.degree)
            new_root.keys = [split_key]
            new_root.children = [self.root, new_node]
            self.root = new_root

    def search(self, key):
        result = self.root.search(key, print_path=True)

        if result is None:
            print("NOT FOUND")
        else:
            return result

    def range_search(self, min_key, max_key):
        results = self.root.range_search(min_key, max_key)

        if results:
            for key, value in results:
                print(f"{key},{value}")

    def delete(self, key):
        self.root.delete(key)

        if len(self.root.keys) == 0 and len(self.root.children) > 0:
            self.root = self.root.children[0]


class Node:
    def __init__(self, degree):
        self.keys = []
        self.values = []
        self.children = []
        self.next = None
        self.degree = degree

        self.MIN_CHILDREN = ceil(self.degree / 2)
        self.MIN_KEYS = self.MIN_CHILDREN - 1
        self.MAX_CHILDREN = self.degree
        self.MAX_KEYS = self.MAX_CHILDREN - 1

    def insert(self, key, value):
        if leaf(self):
            index = bisect.bisect_left(self.keys, key)

            self.keys.insert(index, key)
            self.values.insert(index, value)

            if full(self, self.MAX_KEYS):
                return self.split()
            return None

        if internal(self):
            index = bisect.bisect_left(self.keys, key)

            if index < len(self.keys) and self.keys[index] == key:
                result = self.children[index + 1].insert(key, value)
            else:
                result = self.children[index].insert(key, value)

            # 자식 노드에서 분할이 일어났을 때 처리
            if result:
                split_key, new_node = result
                self.keys.insert(index, split_key)
                self.children.insert(index + 1, new_node)

                if full(self, self.MAX_KEYS):
                    return self.split()
            return None

    def split(self):
        mid = len(self.keys) // 2

        new_node = Node(self.degree)
        new_node.keys = self.keys[mid:]
        new_node.values = self.values[mid:]
        self.keys = self.keys[:mid]
        self.values = self.values[:mid]

        if internal(self):
            new_node.children = self.children[mid + 1 :]
            self.children = self.children[: mid + 1]

        if leaf(self):
            # TODO: next가 맞는지 확인
            new_node.next = self.next
            self.next = new_node

        return new_node.keys[0], new_node

    def search(self, key, print_path=False):
        node = self.search_node(key, print_path=True)
        value = None

        if node is not None and key in node.keys:
            value = node.values[node.keys.index(key)]
            print(node.values[node.keys.index(key)])
        return value

    def range_search(self, min_key, max_key):
        results = []
        node = self.search_node(min_key)

        while node is not None:
            for i in range(len(node.keys)):
                if min_key <= node.keys[i] <= max_key:
                    results.append((node.keys[i], node.values[i]))
                elif min_key > node.keys[i] or node.keys[i] > max_key:
                    return results
            node = node.next
        return results

    def search_node(self, key, print_path=False):
        index = bisect.bisect_left(self.keys, key)

        if internal(self):
            if print_path:
                print(",".join(map(str, self.keys)))
            # 동일한 키라면 오른쪽에 보관하였으므로
            if index < len(self.keys) and self.keys[index] == key:
                return self.children[index + 1].search_node(key)
            else:
                return self.children[index].search_node(key)

        if leaf(self):
            return self

    def delete(self, key, parent=None, index_in_parent=None):
        if leaf(self):
            if key in self.keys:
                index = self.keys.index(key)
                self.keys.pop(index)
                self.values.pop(index)
                if len(self.keys) < self.MIN_KEYS:
                    if parent:
                        return self.rebalance(parent, index_in_parent)
                    elif len(self.keys) == 0:
                        return DeleteStatus.UNDERFLOW
            return DeleteStatus.OK
        if internal(self):
            index = bisect.bisect_left(self.keys, key)
            result = self.children[index].delete(key, self, index)
            if result == DeleteStatus.UNDERFLOW:
                self.children.pop(index)
                if len(self.children) < self.MIN_CHILDREN:
                    if parent:
                        return self.rebalance(parent, index_in_parent)
                    else:
                        if len(self.children) == 1:
                            # 루트 노드가 자식이 하나만 남았을 때
                            self.keys = self.children[0].keys
                            self.values = self.children[0].values
                            self.children = self.children[0].children
                        return DeleteStatus.OK
            if result == DeleteStatus.MERGE:
                # 병합된 경우 키를 삭제
                if index < len(self.keys):
                    self.keys.pop(index)
                else:
                    self.keys.pop()
            return result

    def rebalance(self, parent, index_in_parent):
        # 왼쪽 형제에서 빌리기
        if index_in_parent > 0:
            left_sibling = parent.children[index_in_parent - 1]
            if len(left_sibling.keys) > self.MIN_KEYS:
                if leaf(self):
                    self.keys.insert(0, left_sibling.keys.pop())
                    self.values.insert(0, left_sibling.values.pop())
                    parent.keys[index_in_parent - 1] = self.keys[0]
                if internal(self):
                    self.keys.insert(0, parent.keys[index_in_parent - 1])
                    parent.keys[index_in_parent - 1] = left_sibling.keys.pop()
                    self.children.insert(0, left_sibling.children.pop())
                return DeleteStatus.OK
        # 오른쪽 형제에서 빌리기
        if index_in_parent < len(parent.children) - 1:
            right_sibling = parent.children[index_in_parent + 1]
            if len(right_sibling.keys) > self.MIN_KEYS:
                if leaf(self):
                    self.keys.append(right_sibling.keys.pop(0))
                    self.values.append(right_sibling.values.pop(0))
                    parent.keys[index_in_parent] = right_sibling.keys[0]
                if internal(self):
                    self.keys.append(parent.keys[index_in_parent])
                    parent.keys[index_in_parent] = right_sibling.keys.pop(0)
                    self.children.append(right_sibling.children.pop(0))
                return DeleteStatus.OK
        # 형제와 병합 필요
        if index_in_parent > 0:
            # 왼쪽 형제와 병합
            left_sibling = parent.children[index_in_parent - 1]
            if leaf(self):
                left_sibling.keys.extend(self.keys)
                left_sibling.values.extend(self.values)
                left_sibling.next = self.next
            if internal(self):
                left_sibling.keys.append(parent.keys[index_in_parent - 1])
                left_sibling.keys.extend(self.keys)
                left_sibling.children.extend(self.children)
            parent.children.pop(index_in_parent)
            return DeleteStatus.MERGE
        else:
            # 오른쪽 형제와 병합
            right_sibling = parent.children[index_in_parent + 1]
            if leaf(self):
                self.keys.extend(right_sibling.keys)
                self.values.extend(right_sibling.values)
                self.next = right_sibling.next
            if internal(self):
                self.keys.append(parent.keys[index_in_parent])
                self.keys.extend(right_sibling.keys)
                self.children.extend(right_sibling.children)
            parent.children.pop(index_in_parent + 1)
            return DeleteStatus.MERGE


def save_to_file(bptree, filename):
    with open(filename, "wb") as file:
        pickle.dump(bptree, file)


def load_from_file(filename):
    with open(filename, "rb") as file:
        return pickle.load(file)


def create_index_file(filename, degree):
    bptree = BPTree(degree)

    save_to_file(bptree, filename)


def insert_from_csv(index_file, data_file):
    if os.path.exists(index_file):
        bptree = load_from_file(index_file)

    # CSV 파일에서 키-값 쌍을 읽어와 삽입
    with open(data_file, newline="") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            key, value = int(row[0]), int(row[1])
            bptree.insert(key, value)

    # 삽입 후 B+ 트리 파일을 갱신
    save_to_file(bptree, index_file)


def delete_from_csv(index_file, data_file):
    if os.path.exists(index_file):
        bptree = load_from_file(index_file)

    # CSV 파일에서 키 읽기 및 삭제
    with open(data_file, newline="") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            key = int(row[0])
            bptree.delete(key)

    # 삭제 후 B+ 트리 파일을 갱신
    save_to_file(bptree, index_file)


def search_from_csv(index_file, key):
    if os.path.exists(index_file):
        bptree = load_from_file(index_file)

    bptree.search(key)


def range_search_from_csv(index_file, min_key, max_key):
    if os.path.exists(index_file):
        bptree = load_from_file(index_file)

    bptree.range_search(min_key, max_key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        metavar=("index_file", "b"),
        type=str,
        nargs=2,
    )
    parser.add_argument(
        "-i",
        metavar=("index_file", "data_file"),
        type=str,
        nargs=2,
    )
    parser.add_argument(
        "-d",
        metavar=("index_file", "data_file"),
        type=str,
        nargs=2,
    )
    parser.add_argument(
        "-s",
        metavar=("index_file", "key"),
        type=str,
        nargs=2,
    )
    parser.add_argument(
        "-r",
        metavar=("index_file", "min_key", "max_key"),
        type=str,
        nargs=3,
    )

    args = parser.parse_args()

    if args.c:
        index_file, node_size = args.c
        degree = int(node_size)
        create_index_file(index_file, degree)
    if args.i:
        index_file, data_file = args.i
        insert_from_csv(index_file, data_file)
    if args.d:
        index_file, data_file = args.d
        delete_from_csv(index_file, data_file)
    if args.s:
        index_file, key = args.s
        search_from_csv(index_file, int(key))
    if args.r:
        index_file, min_key, max_key = args.r
        range_search_from_csv(index_file, int(min_key), int(max_key))


if __name__ == "__main__":
    main()
