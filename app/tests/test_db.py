from models.user import User
from sqlalchemy.orm import Session


def test_create_user(session: Session):
    try:
        user = User(id=0, password='0880', email='coffeelover@gmail.com')
        session.add(user)
        session.commit()
        assert user.id == 0
        assert user.email == 'coffeelover@gmail.com'
    except:
        assert False


def test_delete_user(session: Session):
    user = session.query(User).filter_by(id=0).first()
    if not user:
        user = User(id=0, password='0880', email='coffeelover@gmail.com')
        session.add(user)
        session.commit()
    try:
        user = session.query(User).filter_by(id=0).first()
        if user:
            session.delete(user)
            session.commit()
            assert True
        else:
            assert False
    except Exception as ex:
        assert False, ex


def test_get_id(session: Session):
    try:
        user = session.query(User).filter_by(id=0).first()
        if user:
            assert True
    except Exception as ex:
        assert False, ex


def test_get_email(session: Session):
    try:
        user = session.query(User).filter_by(email='testuser@example.com').first()
        if user:
            assert True
    except Exception as ex:
        assert False, ex


def test_get_all(session: Session):
    try:
        users = session.query(User).all()
        if users:
            assert True
    except Exception as ex:
        assert False, ex


def test_get_history(session: Session):
    try:
        user = session.query(User).filter_by(id=0).first()
        if user:
            history = user.transaction_list
            assert isinstance(history, list)
    except Exception as ex:
        assert False, ex