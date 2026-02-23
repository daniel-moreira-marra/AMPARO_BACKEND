import pytest

from core.exceptions import domain as domain_exceptions
from posts.models import PostComment
from posts.services.post_comment_services import (
    create_post_comment,
    delete_post_comment,
    update_post_comment,
)

pytestmark = pytest.mark.django_db


def test_create_post_comment_success(create_user, create_post):
    author = create_user(email="comment_author@example.com")
    actor = create_user(email="comment_actor@example.com")
    post = create_post(author=author, text="Post para comentar", comments_count=0)

    created_comment = create_post_comment(
        actor=actor,
        post_id=post.id,
        content="Comentário válido",
    )

    post.refresh_from_db()
    assert created_comment.user_id == actor.id
    assert created_comment.post_id == post.id
    assert created_comment.content == "Comentário válido"
    assert post.comments_count == 1
    assert PostComment.objects.filter(user=actor, post=post).count() == 1


def test_create_post_comment_not_found_raises_not_found(create_user):
    actor = create_user(email="comment_not_found_actor@example.com")

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        create_post_comment(actor=actor, post_id=999999, content="Comentário")

    assert excinfo.value.code == "post_not_found"


def test_create_post_comment_increments_counter_once_per_comment(create_user, create_post):
    author = create_user(email="comment_counter_author@example.com")
    actor = create_user(email="comment_counter_actor@example.com")
    post = create_post(author=author, text="Post contador", comments_count=0)

    create_post_comment(actor=actor, post_id=post.id, content="Primeiro")
    create_post_comment(actor=actor, post_id=post.id, content="Segundo")

    post.refresh_from_db()
    assert post.comments_count == 2
    assert PostComment.objects.filter(post=post).count() == 2


def test_update_post_comment_success_for_comment_owner(create_user, create_post):
    post_author = create_user(email="update_post_author@example.com")
    comment_author = create_user(email="update_comment_author@example.com")
    post = create_post(author=post_author, text="Post para update")
    comment = PostComment.objects.create(user=comment_author, post=post, content="Antes")

    updated_comment = update_post_comment(
        actor=comment_author,
        post_id=post.id,
        comment_id=comment.id,
        content="Depois",
    )

    comment.refresh_from_db()
    assert updated_comment.id == comment.id
    assert comment.content == "Depois"


def test_update_post_comment_success_for_staff(create_user, create_post):
    post_author = create_user(email="update_staff_post_author@example.com")
    comment_author = create_user(email="update_staff_comment_author@example.com")
    staff_user = create_user(email="update_staff@example.com", is_staff=True)
    post = create_post(author=post_author, text="Post para update")
    comment = PostComment.objects.create(user=comment_author, post=post, content="Antes")

    update_post_comment(
        actor=staff_user,
        post_id=post.id,
        comment_id=comment.id,
        content="Atualizado por staff",
    )

    comment.refresh_from_db()
    assert comment.content == "Atualizado por staff"


def test_update_post_comment_denied_for_post_owner_when_not_comment_owner(create_user, create_post):
    post_author = create_user(email="update_denied_post_author@example.com")
    comment_author = create_user(email="update_denied_comment_author@example.com")
    post = create_post(author=post_author, text="Post para update")
    comment = PostComment.objects.create(user=comment_author, post=post, content="Antes")

    with pytest.raises(domain_exceptions.PermissionDenied) as excinfo:
        update_post_comment(
            actor=post_author,
            post_id=post.id,
            comment_id=comment.id,
            content="Tentativa",
        )

    comment.refresh_from_db()
    assert excinfo.value.code == "comment_permission_denied"
    assert comment.content == "Antes"


def test_update_post_comment_not_found_for_wrong_post_context(create_user, create_post):
    post_author = create_user(email="update_context_post_author@example.com")
    comment_author = create_user(email="update_context_comment_author@example.com")
    post = create_post(author=post_author, text="Post A")
    other_post = create_post(author=post_author, text="Post B")
    comment = PostComment.objects.create(user=comment_author, post=other_post, content="Antes")

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        update_post_comment(
            actor=comment_author,
            post_id=post.id,
            comment_id=comment.id,
            content="Tentativa",
        )

    assert excinfo.value.code == "post_comment_not_found"


def test_update_post_comment_not_found_post(create_user):
    actor = create_user(email="update_missing_post_actor@example.com")

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        update_post_comment(
            actor=actor,
            post_id=999999,
            comment_id=1,
            content="Tentativa",
        )

    assert excinfo.value.code == "post_not_found"


def test_delete_post_comment_success_for_comment_owner(create_user, create_post):
    post_author = create_user(email="delete_post_author@example.com")
    comment_author = create_user(email="delete_comment_author@example.com")
    post = create_post(author=post_author, text="Post para delete", comments_count=1)
    comment = PostComment.objects.create(user=comment_author, post=post, content="Comentário")

    delete_post_comment(
        actor=comment_author,
        post_id=post.id,
        comment_id=comment.id,
    )

    post.refresh_from_db()
    assert post.comments_count == 0
    assert not PostComment.objects.filter(id=comment.id).exists()


def test_delete_post_comment_success_for_post_owner(create_user, create_post):
    post_author = create_user(email="delete_owner_post_author@example.com")
    comment_author = create_user(email="delete_owner_comment_author@example.com")
    post = create_post(author=post_author, text="Post para delete", comments_count=1)
    comment = PostComment.objects.create(user=comment_author, post=post, content="Comentário")

    delete_post_comment(
        actor=post_author,
        post_id=post.id,
        comment_id=comment.id,
    )

    post.refresh_from_db()
    assert post.comments_count == 0
    assert not PostComment.objects.filter(id=comment.id).exists()


def test_delete_post_comment_success_for_staff(create_user, create_post):
    post_author = create_user(email="delete_staff_post_author@example.com")
    comment_author = create_user(email="delete_staff_comment_author@example.com")
    staff_user = create_user(email="delete_staff@example.com", is_staff=True)
    post = create_post(author=post_author, text="Post para delete", comments_count=1)
    comment = PostComment.objects.create(user=comment_author, post=post, content="Comentário")

    delete_post_comment(
        actor=staff_user,
        post_id=post.id,
        comment_id=comment.id,
    )

    post.refresh_from_db()
    assert post.comments_count == 0
    assert not PostComment.objects.filter(id=comment.id).exists()


def test_delete_post_comment_denied_for_third_party(create_user, create_post):
    post_author = create_user(email="delete_denied_post_author@example.com")
    comment_author = create_user(email="delete_denied_comment_author@example.com")
    third_user = create_user(email="delete_denied_third_user@example.com")
    post = create_post(author=post_author, text="Post para delete", comments_count=1)
    comment = PostComment.objects.create(user=comment_author, post=post, content="Comentário")

    with pytest.raises(domain_exceptions.PermissionDenied) as excinfo:
        delete_post_comment(
            actor=third_user,
            post_id=post.id,
            comment_id=comment.id,
        )

    post.refresh_from_db()
    assert excinfo.value.code == "comment_permission_denied"
    assert post.comments_count == 1
    assert PostComment.objects.filter(id=comment.id).exists()


def test_delete_post_comment_not_found_for_wrong_post_context(create_user, create_post):
    post_author = create_user(email="delete_context_post_author@example.com")
    comment_author = create_user(email="delete_context_comment_author@example.com")
    post = create_post(author=post_author, text="Post A")
    other_post = create_post(author=post_author, text="Post B", comments_count=1)
    comment = PostComment.objects.create(user=comment_author, post=other_post, content="Comentário")

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        delete_post_comment(
            actor=comment_author,
            post_id=post.id,
            comment_id=comment.id,
        )

    assert excinfo.value.code == "post_comment_not_found"


def test_delete_post_comment_not_found_post(create_user):
    actor = create_user(email="delete_missing_post_actor@example.com")

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        delete_post_comment(
            actor=actor,
            post_id=999999,
            comment_id=1,
        )

    assert excinfo.value.code == "post_not_found"


def test_delete_post_comment_clamps_counter_to_zero(create_user, create_post):
    post_author = create_user(email="delete_clamp_post_author@example.com")
    comment_author = create_user(email="delete_clamp_comment_author@example.com")
    post = create_post(author=post_author, text="Post para clamp", comments_count=0)
    comment = PostComment.objects.create(user=comment_author, post=post, content="Comentário")

    delete_post_comment(
        actor=comment_author,
        post_id=post.id,
        comment_id=comment.id,
    )

    post.refresh_from_db()
    assert post.comments_count == 0
    assert not PostComment.objects.filter(id=comment.id).exists()


def test_delete_post_comment_repeated_call_keeps_counter_stable(create_user, create_post):
    post_author = create_user(email="delete_repeat_post_author@example.com")
    comment_author = create_user(email="delete_repeat_comment_author@example.com")
    post = create_post(author=post_author, text="Post para repeat", comments_count=1)
    comment = PostComment.objects.create(user=comment_author, post=post, content="Comentário")

    delete_post_comment(
        actor=comment_author,
        post_id=post.id,
        comment_id=comment.id,
    )

    with pytest.raises(domain_exceptions.NotFoundError) as excinfo:
        delete_post_comment(
            actor=comment_author,
            post_id=post.id,
            comment_id=comment.id,
        )

    post.refresh_from_db()
    assert excinfo.value.code == "post_comment_not_found"
    assert post.comments_count == 0
