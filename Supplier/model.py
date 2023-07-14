from sqlalchemy import (
    create_engine,
    ForeignKey,
    Column,
    Integer,
    String,
    TIMESTAMP,
    text,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

Base = declarative_base()
engine = create_engine("sqlite:///resources/telegram.db", echo=True)

"""Instance containing account credentials"""


class Account(Base):
    __tablename__ = "accounts"

    account_telegram_id = Column(String, primary_key=True, nullable=False)
    time_registred = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __init__(self, account_telegram_id):
        self.account_telegram_id = account_telegram_id


"""Instance containing categories information"""


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False, index=True)

    def __init__(self, category_name):
        self.category_name = category_name


class Account_by_category(Base):
    __tablename__ = "accounts_and_categories"
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    account_telegram_id = Column(Integer,  ForeignKey("accounts.account_telegram_id", ondelete="CASCADE"), primary_key=True, index=True, nullable=False)
    is_enabled_for_search = Column(Boolean, nullable=False, default=True)

    def __init__(self, category_id, account_telegram_id, is_enabled_for_search=True):
        self.category_id = category_id
        self.account_telegram_id = account_telegram_id
        self.is_enabled_for_search = is_enabled_for_search


Base.metadata.create_all(bind=engine)
SessionMaker = sessionmaker(bind=engine, expire_on_commit=False)
