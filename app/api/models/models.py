from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean , UniqueConstraint
from sqlalchemy.orm import relationship


from api.db.DataBasse import Base


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    gmail = Column(String, unique=True, index=True)
    password = Column(String)
    posts = relationship('PostModel', back_populates='author')


class PostModel(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    created_at = Column(DateTime)
    author_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"),)
    image = relationship('ImageModel', back_populates='posts')
    author = relationship('UserModel', back_populates='posts')
    likes = relationship('LikeModel', backref='post')


class ImageModel(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"))
    posts = relationship("PostModel", back_populates="image")


class LikeModel(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"))
    is_liked = Column(Boolean)
    __table_args__ = (
        UniqueConstraint("user_id", "post_id"),
    )
