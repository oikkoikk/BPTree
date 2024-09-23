# B+ tree

컴퓨터소프트웨어학부 2020018159 이종준

## 1. 요약

데이터베이스에서 효율적인 인덱싱을 위해 사용되는 B+ 트리를 python으로 구현하였습니다.

`pickle` 모듈을 사용해 트리를 파일에 저장하거나 파일에서 불러와서 사용하도록 하였습니다.

삽입, 삭제, 검색을 재귀적으로 동작하도록 구현하였습니다. 따라서 python의 재귀 호출 깊이 제한을 1,000,000으로 설정해주었습니다.

## 2. 함수별 코드 설명

### `BPTree` 클래스

해당 클래스는 B+ 트리의 구현체로, 루트 `Node`를 관리하고 삽입(`insert()`), 삭제(`delete()`), 검색(`search()`), 범위 검색(`range_search()`) 연산을 구현하였습니다.

- **`__init__(self, degree)`**: B+ 트리를 커맨드라인에서 입력받은 차수로 초기화합니다. 차수는 각 노드가 가질 수 있는 최대 key와 자식 노드의 수를 결정합니다.
<br>

- **`insert(self, key, value)`**: key-value 쌍을 B+ 트리에 삽입합니다. 루트 노드에서 분할이 발생하면 새로운 루트 노드를 생성하게 됩니다.
<br>

- **`search(self, key)`**: 특정 key를 B+ 트리에서 검색합니다. 검색 과정에서 경유하는 노드의 key 값을 출력하고, 검색 결과가 있다면 해당 노드의 value를, 없다면 "NOT FOUND"를 출력합니다.
<br>

- **`range_search(self, min_key, max_key)`**: `min_key`와 `max_key` 사이의 key-value 쌍을 검색하고, 결과값을 key,value 양식으로 출력합니다.
<br>

- **`delete(self, key)`**: 주어진 key를 B+ 트리에서 삭제합니다. 루트가 비어 있으면 트리의 구조를 재조정하여 균형을 잡습니다.

### `Node` 클래스

B+ 트리의 각 노드를 나타냅니다. key와 value를 하나의 클래스에 보관하지 않고 각각의 list에 보관하여 인덱스를 기반으로 접근할 수 있도록 구현하였습니다. leaf 노드와 internal 노드를 따로 구현하지 않고 공통적으로 `Node` 클래스를 사용할 수 있도록 하여 단순한 구조를 가질 수 있도록 하였습니다.

degree를 바탕으로, `MIN_CHILDREN`, `MIN_KEYS`와 같은 자주 사용되는 값들을 상수화하여 편의성을 높였습니다.

- **`__init__(self, degree)`**: 주어진 차수를 넘겨받아 새 노드를 초기화합니다. 또한 최소 및 최대 key, 자식 수를 설정합니다.
<br>
  
- **`insert(self, key, value)`**: 노드에 key-value 쌍을 삽입합니다. 노드가 가득 차면 분할하여 균형을 잡습니다.
<br>
  
- **`split(self)`**: 노드를 두 개로 분할하고, 중간 key와 새로 생성된 오른쪽 노드를 반환합니다. 내부 노드의 경우 중간 key는 부모 노드로 올라가게 됩니다.
<br>

- **`search(self, key)`**: 현재 노드에서 key를 검색합니다. 검색 과정에서 경유하는 노드의 key 값을 출력하도록 search_node()에 `print_path`를 True로 넘겨줍니다.
<br>

- **`range_search(self, min_key, max_key)`**: 현재 노드에서 범위 검색을 수행합니다. 적절한 노드를 찾으면 leaf 노드의 `next` 포인터를 따라 검색을 계속하게 됩니다.
<br>

- **`delete(self, key, parent=None, index_in_parent=None)`**: 노드에서 주어진 key를 삭제합니다. 노드가 부족할 경우(key가 너무 적을 경우) 형제 노드에서 key를 빌리거나 형제 노드와 병합하여 균형을 잡습니다. 이 과정에서 `DeleteStatus` 열거형을 사용해 삭제 상태를 반환하는데, `DeleteStatus.OK`는 정상 삭제, `DeleteStatus.UNDERFLOW`는 노드가 최소 키 개수 미만으로 감소한 상태, `DeleteStatus.MERGE`는 병합이 발생한 상태를 나타냅니다.
<br>

  - **`rebalance(self, parent, index_in_parent)`**: 삭제 후 트리의 균형을 맞춥니다. 형제 노드에서 key를 빌리거나 형제 노드와 병합하여 균형을 잡습니다. 재조정이 성공적으로 완료되면 `DeleteStatus.OK`를 반환하며, 병합이 일어난 경우에는 `DeleteStatus.MERGE`를 반환합니다.

### **기타 유틸리티 함수**

- **`leaf(node)`**: 주어진 노드가 leaf 노드인지 확인하는 함수입니다. leaf 노드는 자식 노드가 없으므로, node.children의 길이가 0인 경우에 leaf 노드로 간주합니다.
<br>

- **`internal(node)`**: 주어진 노드가 internal 노드인지 확인하는 함수입니다. internal 노드는 하나 이상의 자식 노드를 갖고 있으므로, node.children의 길이가 0보다 큰 경우에 internal 노드로 간주합니다.
<br>

- **`full(node, MAX_KEYS)`**: 주어진 노드가 key로 가득 찼는지 확인하는 함수입니다. 노드가 가득 차면 더 이상 새로운 key를 삽입할 수 없으므로, node.keys의 길이가 `MAX_KEYS`와 동일한 경우에 노드가 가득 찬 것으로 간주합니다.
<br>

- **`save_to_file(bptree, filename)`**: `pickle`을 사용해 B+ 트리를 파일에 저장합니다.
<br>

- **`load_from_file(filename)`**: `pickle`을 사용해 파일에서 B+ 트리를 불러옵니다.
<br>

- **`create_index_file(filename, degree)`**: 주어진 차수로 빈 B+ 트리를 초기화하고 파일에 저장합니다.
<br>

- **`insert_from_csv(index_file, data_file)`**: CSV 파일에서 key-value 쌍을 읽어와서 B+ 트리에 삽입합니다.
<br>

- **`delete_from_csv(index_file, data_file)`**: CSV 파일에서 key를 읽어와서 B+ 트리에서 삭제합니다.
<br>

- **`search_from_csv(index_file, key)`**: 파일에 저장된 B+ 트리에서 특정 key를 검색합니다.
<br>

- **`range_search_from_csv(index_file, min_key, max_key)`**: 파일에 저장된 B+ 트리에서 범위 검색을 수행합니다.
<br>

## 3. 코드 실행 방법

프로그램을 실행하려면 명령어를 사용하여 인덱스를 생성하고, 데이터를 삽입하거나 삭제하거나, 검색을 수행할 수 있습니다.

**명령어 사용법:**

- **인덱스 파일 생성:**

  ```bash
  python bptree.py -c <index_file> <degree>
  ```

- **CSV 파일에서 삽입:**

  ```bash
  python bptree.py -i <index_file> <data_file>
  ```

- **CSV 파일에서 삭제:**

  ```bash
  python bptree.py -d <index_file> <data_file>
  ```

- **키 검색:**

  ```bash
  python bptree.py -s <index_file> <key>
  ```

- **키 범위 검색:**

  ```bash
  python bptree.py -r <index_file> <min_key> <max_key>
  ```

**index 파일 형식:**

- `.dat` 포맷의 파일을 생성합니다

**CSV 파일 형식:**

- 삽입의 경우 CSV 파일의 각 행은 (키, 값) 두 개의 열을 가져야 하며, 삭제의 경우 키만 입력되어야 합니다.
