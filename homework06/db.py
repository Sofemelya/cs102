from scraputils import get_news
from sqlalchemy import Column, Integer, String, create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

Base = declarative_base()  # type: ignore
engine = create_engine("sqlite:///news.db")  # type: ignore
session = sessionmaker(bind=engine)  # type: ignore


class News(Base):  # type: ignore
    __tablename__ = "news"  # type: ignore
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    s = session()
    news_list = get_news("https://news.ycombinator.com/newest", n_pages=35)
    for sg in range(len(news_list)):
        news = News(
            title=news_list[sg]["title"],
            author=news_list[sg]["author"],
            url=news_list[sg]["url"],
            comments=news_list[sg]["comments"],
            points=news_list[sg]["points"],
        )
        s.add(news)
        s.commit()