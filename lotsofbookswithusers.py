from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Book, User

engine = create_engine('sqlite:///booksapp.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Books for "Young Adult" category
category1 = Category(user_id=1, name="Young Adult")

session.add(category1)
session.commit()

book1 = Book(user_id=1, name="The Hunger Games", description="Could you survive on your own, in the wild, with everyone out to make sure you don't live to see the morning",
                     author="Suzanne Collins", category=category1)

session.add(book1)
session.commit()


book2 = Book(user_id=1, name="Harry Potter and the Order of the Phoenix", description="There is a door at the end of a silent corridor. And it's haunting Harry Potter's dreams. Why else would he be waking in the middle of the night, screaming in terror",
                     author="J.K. Rowling", category=category1)

session.add(book2)
session.commit()

book3 = Book(user_id=1, name="Opposite of Always", description="When Jack and Kate meet at a party, bonding until sunrise over their mutual love of Froot Loops and their favorite flicks, Jack knows he's falling-hard.",
                     author="Justin A. Reynolds", category=category1)

session.add(book3)
session.commit()

book4 = Book(user_id=1, name="Superman: Dawnbreaker", description="Clark Kent has always been faster, stronger--better--than everyone around him. But he wasn't raised to show off, and drawing attention to himself could be dangerous.",
                     author="Matt de la Pena", category=category1)

session.add(book4)
session.commit()

# Books for "Classic" category
category2 = Category(user_id=1, name="Classic")

session.add(category2)
session.commit()


book1 = Book(user_id=1, name="The Little Prince", description="Moral allegory and spiritual autobiography, The Little Prince is the most translated book in the French language.",
                     author="Antoine de Saint-Exupery", category=category2)

session.add(book1)
session.commit()

book2 = Book(user_id=1, name="And Then There Were None",
                     description="First, there were ten-a curious assortment of strangers summoned as weekend guests to a private island off the coast of Devon.", author="Agatha Christie",category=category2)

session.add(book2)
session.commit()

book3 = Book(user_id=1, name="The Great Gatsby", description="THE GREAT GATSBY, F. Scott Fitzgerald's third book, stands as the supreme achievement of his career. ",
                     author="F. Scott Fitzgerald", category=category2)

session.add(book3)
session.commit()


# Books for "Fiction" category
category3 = Category(user_id=1, name="Fiction")

session.add(category3)
session.commit()


book1 = Book(user_id=1, name="Queenie", description="Bridget Jones's Diary meets Americanah in this disarmingly honest, boldly political, and truly inclusive novel that will speak to anyone who has gone looking for love and found something very different in its place.",
                     author="Candice Carty-Williams", category=category3)

session.add(book1)
session.commit()

book2 = Book(user_id=1, name="The Bird King", description="Set in 1491 during the reign of the last sultanate in the Iberian peninsula, The Bird King is the story of Fatima, the only remaining Circassian concubine to the sultan, and her dearest friend Hassan, the palace mapmaker. ",
                     author="G. Willow Wilson", category=category3)

session.add(book2)
session.commit()
print('books added to db')