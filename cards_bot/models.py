from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from cards_bot.database import Base

class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(Text)
    author_id = Column(Integer)
    cards = relationship("Card", back_populates="deck", cascade="all, delete")

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    term = Column(String(100))
    answer = Column(Text)
    deck_id = Column(Integer, ForeignKey("decks.id"))
    deck = relationship("Deck", back_populates="cards")
