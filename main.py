# Fast API같은 서드파티 라이브러리보다, 표준 Python에서 제공되기 떄문에 위에 from typing import Annotated를 선언해주어야 한다.
from typing import Annotated

from fastapi import FastAPI, status, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import AfterValidator

app = FastAPI(title="Rent-a-Room API",
              description="API for managing room rentals",
              version="1.0.0",
              contact={
                  "name": "Yun",
                  "email": "yun.email@example.com"
              })

# 앞의 /assets는 URL 경로, 뒤의 directory는 실제 파일 경로를 의미한다.(둘이 같을 필요 x)
# 즉, /assets로 들어오는 요청은 assets 폴더에서 정적 파일을 찾도록 한다.
# name은 FastAPI 내부에서 사용하는 이름으로, URL 경로와 실제 파일 경로를 연결하는 역할을 한다.
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


house = {
        "id": 1,
        "name": "Cozy 3-bedroom house",
        "price_per_night": 350,
        "bedrooms": 3,
        "bathrooms": 2.5,
    }

apartment = {   
        "id": 2,
        "name": "Cozy Apartment",
        "price_per_night": 200,
        "bedrooms": 2,
        "bathrooms": 1,
    }

studio = {
        "id": 3,
        "name": "Modern Studio",
        "price_per_night": 150,
        "bedrooms": 1,
        "bathrooms": 1,
    }

# Query를 변수로 선언해서 재사용할 수 있다.
search_query_validation = Query(
    min_length=3,
    max_length=10,
    title="Search term",
    description="Provide a keyword to look for within the room's title"
)

def fail_if_funny(search: str):
    if "lol" in search:
        raise ValueError("No funny business allowed")
    return search

# AfterValidator를 변수로 선언해서 재사용할 수 있다.
search_humor_ban_validation = AfterValidator(fail_if_funny)

# 검색 쿼리 파라미터의 타입과 검증 규칙을 묶어 재사용한다.(추가로 여기는 Annotated만 사용할 뿐, 기본값은 None으로 설정해줘야 한다.)
SearchQuery = Annotated[
    str | None, search_query_validation, search_humor_ban_validation]





@app.get("/", status_code=200 or status.HTTP_200_OK)
def root():
    return {"message": "Welcome to the Rent-a-Room API!"}


# 함수 인자만 → Query parameter
@app.get("/rooms", status_code=status.HTTP_200_OK)
def get_rooms(                                                                                                                                                                                                                # 이 AFterValidator는 앞선 Query에서 min_length와 max_length를 만족하는지 검증한 후, 통과됐다는 전제로 진행한다.
    max_price: Annotated[int | None, Query(ge=10, le=10_000)]=None, search: Annotated[str | None, Query(min_length=3, max_length=10, title="Search term", description="Provide a keyword to look for within the room's title"), AfterValidator(fail_if_funny)] = None):  # 참고로 기본값이 없는 쿼리 파라미터는, 기본값이 있는 쿼리 파라미터보다 먼저 선언되어야 한다.
    results = [house, apartment, studio]

    if max_price:
        results = [room for room in results if room["price_per_night"] <= max_price]

    if search:
        results = [room for room in results if search.lower() in room["name"].lower()]

    return results

# 리팩토링 추가한 것, 위에랑 Query랑 AfterValidator는 동일함
@app.get("/rooms/mansions", status_code=status.HTTP_200_OK)
def get_rooms(                                                                                                                                                                                                               
    max_price: Annotated[int | None, Query(ge=10, le=10_000)]=None,
    search: SearchQuery = None):  # 참고로 기본값이 없는 쿼리 파라미터는, 기본값이 있는 쿼리 파라미터보다 먼저 선언되어야 한다.
    results = [house, apartment, studio]

    if max_price:
        results = [room for room in results if room["price_per_night"] <= max_price]

    if search:
        results = [room for room in results if search.lower() in room["name"].lower()]

    return results


""" # 위에 app.mount를 선언했기 때문에, /assets로 들어오는 요청은 assets 폴더에서 정적 파일을 찾도록 한다.
@app.get("/rooms/faq", status_code=status.HTTP_200_OK)
def get_room_faq():
    return {
        "check-in": "From 3PM",
        "check-out": "Until 12PM"
    }  """

# {} + 함수 인자 → Path parameter
@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK)
# int가 아닌 것을 파라미터로 받으면 422 Unprocessable Entity를 반환한다. 즉, int로 받도록 강제한다 ex) /rooms/1.5 → 422 Unprocessable Entity
def get_rooms(room_id: int):
    for room in [house, apartment, studio]:
        if room["id"] == room_id:
            return room

        # 이게 없으면 room을 4번 이상 요청했을 때, 200 OK를 반환하고 None을 반환하게 된다. 따라서 404 Not Found를 반환하도록 예외처리를 해주어야 한다. 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

""" # 이렇게 되면, faq가 위의 {room_id}에 걸려서 /rooms/faq로 요청했을 때 422 Unprocessable Entity를 반환하게 된다. 따라서 faq를 먼저 선언해주어야 한다.(Route order matters)
@app.get("/rooms/faq", status_code=status.HTTP_200_OK)
def get_room_faq():
    return {
        "check-in": "From 3PM",
        "check-out": "Until 12PM"
    } """