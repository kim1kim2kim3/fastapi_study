# 이 Annotated는 Fast API 안에 있는게 아니라, Python 자체에서 제공하는 기능입니다. 이 메타데이터를 붙임으로써, Fast API가 이 메타데이터를 읽고, 해당 파라미터에 대한 제약 조건을 적용할 수 있습니다.
# 예를 들어, min_length와 max_length를 지정하면, Fast API는 해당 파라미터의 길이를 검증할 수 있습니다.
from typing import Annotated, get_type_hints

def QuerypParamneterConstraint(min_length: int = 0, max_length: int =50):
    return {"min_length": min_length, "max_length": max_length}


def my_function(value: Annotated[str, 'Hello', QuerypParamneterConstraint(10, 30)]):
    print(value)

my_function("Hello, this is a test string.")

# Fast Api 서버가 시작될 때마다, 아래처럼 개념적으로 Fast API는 my_function의 파라미터에 대한 타입 힌트를 읽고, Annotated에 포함된 메타데이터를 확인합니다.
# 이를 통해 Fast API는 해당 파라미터에 대한 제약 조건을 적용할 수 있습니다.
hints = get_type_hints(my_function, include_extras=True)
print(hints['value'].__metadata__)