import pytest

from core.exceptions import domain as domain_exceptions
from posts.models import PostLike
from posts.services.post_like_services import like_post, unlike_post

pytestmark = pytest.mark.django_db


def test_like_post_success(create_user, create_post):
    author = create_user(email="like_author@example.com")
    actor = create_user(email="like_actor@example.com")
    post = create_post(author=author, text="Post para curtir")

    created_like = like_post(actor=actor, post_id=post.id)

    post.refresh_from_db()
    assert created_like.user_id == actor.id
    assert created_like.post_id == post.id
    assert post.likes_count == 1
    assert PostLike.objects.filter(user=actor, post=post).exists()


def test_like_post_duplicate_raises_conflict(create_user, create_post):
    author = create_user(email="dup_author@example.com")
    actor = create_user(email="dup_actor@example.com")
    post = create_post(author=author, text="Post para curtir duas vezes")

    like_post(actor=actor, post_id=post.id)

    with pytest.raises(domain_exceptions.ConflictError) as excinfo:
        like_post(actor=actor, post_id=post.id)

    post.refresh_from_db()
    assert excinfo.value.code == "post_already_liked"
    assert post.likes_count == 1
    assert PostLike.objects.filter(user=actor, post=post).count() == 1


def test_like_post_not_found_raises_not_found(create_user):
    actor = create_user(email="not_found_actor@example.com")

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        like_post(actor=actor, post_id=999999)

    assert excinfo.value.code == "post_not_found"


def test_unlike_post_success(create_user, create_post):
    author = create_user(email="unlike_author@example.com")
    actor = create_user(email="unlike_actor@example.com")
    post = create_post(author=author, text="Post com unlike", likes_count=0)
    like_post(actor=actor, post_id=post.id)

    unlike_post(actor=actor, post_id=post.id)

    post.refresh_from_db()
    assert post.likes_count == 0
    assert not PostLike.objects.filter(user=actor, post=post).exists()


def test_unlike_post_not_found_raises_not_found(create_user):
    actor = create_user(email="unlike_post_missing_actor@example.com")

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        unlike_post(actor=actor, post_id=999999)

    assert excinfo.value.code == "post_not_found"


def test_unlike_post_missing_like_raises_not_found(create_user, create_post):
    author = create_user(email="unlike_missing_author@example.com")
    actor = create_user(email="unlike_missing_actor@example.com")
    post = create_post(author=author, text="Post sem curtida", likes_count=0)

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        unlike_post(actor=actor, post_id=post.id)

    post.refresh_from_db()
    assert excinfo.value.code == "post_like_not_found"
    assert post.likes_count == 0


def test_unlike_post_clamps_likes_count_to_zero(create_user, create_post):
    author = create_user(email="unlike_clamp_author@example.com")
    actor = create_user(email="unlike_clamp_actor@example.com")
    post = create_post(author=author, text="Post clamp", likes_count=0)
    PostLike.objects.create(user=actor, post=post)

    unlike_post(actor=actor, post_id=post.id)

    post.refresh_from_db()
    assert post.likes_count == 0
    assert not PostLike.objects.filter(user=actor, post=post).exists()


def test_unlike_post_repeated_call_keeps_counter_stable(create_user, create_post):
    author = create_user(email="unlike_repeat_author@example.com")
    actor = create_user(email="unlike_repeat_actor@example.com")
    post = create_post(author=author, text="Post repeat unlike", likes_count=0)
    like_post(actor=actor, post_id=post.id)

    unlike_post(actor=actor, post_id=post.id)

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        unlike_post(actor=actor, post_id=post.id)

    post.refresh_from_db()
    assert excinfo.value.code == "post_like_not_found"
    assert post.likes_count == 0
