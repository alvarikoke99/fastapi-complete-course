from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status
app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int, published_date: int):
        self.id = id if id else find_book_id()
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: int | None = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(ge=0, le=5)
    published_date: int = Field(ge=0, le=2024)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2004,
            }
        }
    }


books = [
    Book(1, "Computer Science Pro", "codingwithroby", "A very nice book!", 5, 2024),
    Book(2, "Python for Beginners", "john_doe", "A great book for Python starters!", 4, 2020),
    Book(3, "Mastering Algorithms", "alice_lee", "An advanced book on algorithms.", 5, 2023),
    Book(4, "Data Structures in Depth", "michael_scott", "A comprehensive guide on data structures.", 5, 2024),
    Book(5, "AI and Machine Learning", "sarah_jones", "Learn the basics of AI and ML!", 4, 2021),
    Book(6, "Database Design Simplified", "jane_smith", "A step-by-step guide to designing databases.", 3, 2004),
    Book(7, "Game Development 101", "tom_baker", "Start your journey in game development!", 5, 2005),
    Book(8, "Web Development with JavaScript", "robin_hood", "Create modern web apps with JavaScript.", 4, 2003),
    Book(9, "The Art of Debugging", "linda_kim", "A book dedicated to debugging strategies.", 5, 2024),
    Book(10, "Cloud Computing Essentials", "matt_walker", "Get started with cloud technologies.", 4, 2012)
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return books

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(book_rating: int = Query(ge=0, le=5)):
    books_to_return = []
    for book in books:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_publish_date(book_date: int = Query(ge=0, le=2024)):
    books_to_return = []
    for book in books:
        if book.published_date == book_date:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book_by_id(book_id: int = Path(gt=0)):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookRequest):
    new_book = Book(**book.model_dump())
    books.append(new_book)

@app.put("/books", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(books)):
        if book.id == books[i].id:
            books[i] = Book(**book.model_dump())
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_deleted = False
    for i in range(len(books)):
        if book_id == books[i].id:
            books.pop(i)
            book_deleted = True
            break
    if not book_deleted:
        raise HTTPException(status_code=404, detail="Book not found")

def find_book_id():
    return 1 if len(books) == 0 else books[-1].id + 1
