from imit import app, models, forms, db
import imit.utils as utils
from imit.utils import role_required, flash_errors, get_form_errors, remove_file, first
from flask import render_template, request, redirect, abort
from werkzeug.utils import secure_filename
import os
from sqlalchemy import desc
import base64
from datetime import datetime
import sys

@app.route('/news')
def news_page():
    try:
        year = int(request.args.get("year", datetime.now().year))
        end_year = datetime.strptime(str(year + 1), "%Y")
        year = datetime.strptime(str(year), "%Y")
        year_selected = True
    except ValueError:
        year = datetime.strptime("2016", "%Y")
        end_year = datetime.now()
        year_selected = False

    years = range(2016, datetime.now().year + 1)
    pages = models.Post.query.filter(models.Post.date_created.between(year, end_year)) \
        .order_by(desc(models.Post.date_created))
    images = models.Image.query.filter(models.Image.type_post == "post")
    return render_template('news/news.html', full=True, posts=pages, cur_year=year.year, years=years, year_selected=year_selected, images = images)


@app.route('/news/<nid>')
def news_full_text_page(nid):
    post = models.Post.query.get_or_404(nid)
    images = models.Image.query.filter(models.Image.id_post == post.id)
    return render_template('news/post.html', post=post, images = images)


@app.route('/news/add_vk')
@role_required('editor')
def add_news_vk_list():
    j = utils.get_vk_wall_posts("-46264391", 15)
    vk_posts = [utils.convert_vk_post(p) for p in j]
    return render_template('news/news_vk_pickup.html', vk_posts=vk_posts)


@app.route('/news/add_vk/<pid>')
@role_required('editor')
def add_news_vk(pid):
    edit_form = forms.NewsForm()
    j = utils.get_vk_wall_post(pid, "-46264391")
    post = utils.convert_vk_post(j)
    if j is None:
        abort(404)

    # Passing post data to form fields for editing
    edit_form.title.data = post["title"]
    edit_form.full_text.data = render_template("news/news_vk_pickup_item.html", n=post)
    edit_form.date.data = post["date"].strftime("%d.%m.%Y")

    return render_template("news/add_news.html", add_form=edit_form, post=post, add_file_form=forms.FileForm(),
                           edit_file_form=forms.FileEditForm(), remove_file_form=forms.FileRemoveForm(),
                           action="/news/add")


@app.route('/news/add', methods=('GET', 'POST'))
@role_required('editor')
def add_news():
    add_form = forms.NewsForm()
    if request.method == 'POST':
        if add_form.validate_on_submit():
            type_post = "post"
            post = models.Post()
            add_form.populate_obj(post)
            if add_form.date.data:
                post.date_created = datetime.strptime(add_form.date.data, "%d.%m.%Y")
            post.cover_image = 0
            db.session.add(post)
            db.session.commit()

            # Save cover image if any.
            if add_form.cropped_cover_image_data.data:
                if 'full_cover_image' in request.files:
                    #file = first(request.files.getlist("full_cover_image"))
                    post.cover_image = 1
                    images = request.files.getlist("full_cover_image")
                    i = 1 #счетчик фото для названия
                    for image in images:
                        _save_image(add_form.cropped_cover_image_data.data, image, post, i, type_post)
                        i += 1
                    #if file is not None and not file.filename == '':
                    #    _save_cover_image(add_form.cropped_cover_image_data.data, file, post)
                    #else:
                    #    print("Cropped image is set but full image is not")
                    #    app.logger.warning("Cropped image is set but full image is not")
                else:
                    print("Cropped image is set but full image is not")
                    app.logger.warning("Cropped image is set but full image is not")

            return redirect(f'/news/{post.id}')
        else:
            app.logger.warning(f"Invalid NewsForm input: {get_form_errors(add_form)}")
            flash_errors(add_form)

    return render_template("news/add_news.html",
                           add_form=add_form,
                           add_file_form=forms.FileForm(),
                           edit_file_form=forms.FileEditForm(),
                           remove_file_form=forms.FileRemoveForm()
                           )

@app.route('/news/add/save', methods=('GET', 'POST'))
@role_required('editor')
def add_news_save():
    add_form = forms.NewsForm()
    if request.method == 'POST':
        if add_form.validate_on_submit():
            type_post = "draft_post"
            post = models.Draft_post()
            add_form.populate_obj(post)

            db.session.add(post)
            db.session.commit()

            # Save cover image if any.
            if add_form.cropped_cover_image_data.data:
                if 'full_cover_image' in request.files:
                    #file = first(request.files.getlist("full_cover_image"))
                    post.cover_image = 1
                    images = request.files.getlist("full_cover_image")
                    i = 1 #счетчик фото для названия
                    for image in images:
                        _save_image(add_form.cropped_cover_image_data.data, image, post, i, type_post)
                        i += 1
                    #if file is not None and not file.filename == '':
                    #    _save_cover_image(add_form.cropped_cover_image_data.data, file, post)
                    #else:
                    #    print("Cropped image is set but full image is not")
                    #    app.logger.warning("Cropped image is set but full image is not")
                else:
                    print("Cropped image is set but full image is not")
                    app.logger.warning("Cropped image is set but full image is not")
    return redirect(f'/')

@app.route('/drafts/<nid>/delete')
@role_required('editor')
def delete_draft_news(nid):
    post = models.Draft_post.query.get_or_404(nid)
    app.logger.debug("News with id %s is being deleted", nid)
    # for file in post.files:
    #     if not remove_file(file):
    #         return "Ошибка при удалении файла"
    # # Delete cover image
    # if post.has_cover_image:
    #     _remove_cover_image(post)
    db.session.delete(post)
    db.session.commit()
    return redirect('/drafts')


@app.route('/drafts/<nid>/edit', methods=('GET', 'POST'))
@role_required('editor')
def edit_draft_news(nid):
    edit_form = forms.NewsForm()
    post = models.Draft_post.query.get_or_404(nid).toPost()
    if request.method == 'POST':
        if edit_form.validate_on_submit():
            app.logger.debug("News with id %s is being edited", nid)
            edit_form.populate_obj(post)
            if edit_form.date.data is not None and edit_form.date.data != "":
                post.date_created = datetime.strptime(edit_form.date.data, "%d.%m.%Y")
            db.session.add(post)
            db.session.commit()

            # Delete cover image if any
            if edit_form.delete_cover_image.data and post.has_cover_image:
                _remove_cover_image(post)
            # Save cover image if any.
            if edit_form.cropped_cover_image_data.data:
                if post.has_cover_image:
                    _remove_cover_image(post)
                if 'full_cover_image' in request.files:
                    file = first(request.files.getlist("full_cover_image"))
                    if file is not None and not file.filename == '':
                        _save_cover_image(edit_form.cropped_cover_image_data.data, file, post)
                    else:
                        app.logger.warning("Cropped image is set but full image is not")
                else:
                    app.logger.warning("Cropped image is set but full image is not")
            return redirect('/news')
        else:
            app.logger.debug("Invalid NewsForm input: {}".format(get_form_errors(edit_form)))
            app.logger.debug("{}".format(first(request.files.getlist("full_cover_image"))))
            flash_errors(edit_form)
    # Passing post data to form fields for editing
    edit_form.title.data = post.title
    edit_form.full_text.data = post.full_text
    return render_template("news/add_news.html", add_form=edit_form, post=post, add_file_form=forms.FileForm(),
                           edit_file_form=forms.FileEditForm(), remove_file_form=forms.FileRemoveForm())


@app.route('/news/<nid>/edit', methods=('GET', 'POST'))
@role_required('editor')
def edit_news(nid):
    edit_form = forms.NewsForm()
    post = models.Post.query.get_or_404(nid)
    images = models.Image.query.filter(models.Image.id_post == post.id)
    if request.method == 'POST':
        if edit_form.validate_on_submit():
            type_post = "post"
            app.logger.debug("News with id %s is being edited", nid)
            edit_form.populate_obj(post)
            if edit_form.date.data is not None and edit_form.date.data != "":
                post.date_created = datetime.strptime(edit_form.date.data, "%d.%m.%Y")
            db.session.commit()

            # Delete cover image if any
            if edit_form.delete_cover_image.data and post.cover_image:
                _remove_image(post)
            # Save cover image if any.
            if edit_form.cropped_cover_image_data.data:
                if post.cover_image:
                    _remove_image(post)
                if 'full_cover_image' in request.files:
                    #file = first(request.files.getlist("full_cover_image"))
                    post.cover_image = 1
                    images = request.files.getlist("full_cover_image")
                    i = 1 #счетчик фото для названия
                    for image in images:
                        _save_image(edit_form.cropped_cover_image_data.data, image, post, i, type_post)
                        i += 1
                    #if file is not None and not file.filename == '':
                    #    _save_cover_image(add_form.cropped_cover_image_data.data, file, post)
                    #else:
                    #    print("Cropped image is set but full image is not")
                    #    app.logger.warning("Cropped image is set but full image is not")
                else:
                    print("Cropped image is set but full image is not")
                    app.logger.warning("Cropped image is set but full image is not")
            return redirect('/news/{}'.format(post.id))
        else:
            app.logger.debug("Invalid NewsForm input: {}".format(get_form_errors(edit_form)))
            app.logger.debug("{}".format(first(request.files.getlist("full_cover_image"))))
            flash_errors(edit_form)
    # Passing post data to form fields for editing        
    edit_form.title.data = post.title
    edit_form.full_text.data = post.full_text
    return render_template("news/add_news.html", add_form=edit_form, post=post, add_file_form=forms.FileForm(),
                           edit_file_form=forms.FileEditForm(), remove_file_form=forms.FileRemoveForm(), images = images)


@app.route('/news/<nid>/delete')
@role_required('editor')
def delete_news(nid):
    post = models.Post.query.get_or_404(nid)
    app.logger.debug("News with id %s is being deleted", nid)
    for file in post.files:
        if not remove_file(file):
            return "Ошибка при удалении файла"
    # Delete cover image
    if post.cover_image:
        #_remove_cover_image(post)
        _remove_image(post)
    db.session.delete(post)
    db.session.commit()
    return redirect('/news')

def _save_image(data, file, post, i, type_post):
    app.logger.debug("Adding cover image to news %s", post.id)
    if data is None or post is None:
        app.logger.error("None is not accepted")
        return False
    filename = secure_filename("{}_{}_{}.png".format(type_post, post.id, i))
    fn, file_extension = os.path.splitext(file.filename)
    full_filename = secure_filename("{}_{}_{}_full{}".format(type_post, post.id, i, file_extension))
    try:
        app.logger.debug("Storing images %s and %s to drive", filename, full_filename)
        with open(os.path.join(app.config['FILE_UPLOAD_PATH'], "covers", filename), "wb") as fh:
            fh.write(base64.b64decode(data.split(",")[1]))
        file.save(os.path.join(app.config['FILE_UPLOAD_PATH'], "covers", full_filename))
    except Exception as e:
        app.logger.error('Error ocurried during cover image file saving: %s', e)
        return False
    image = models.Image()
    image.filename = full_filename
    image.type_post = type_post
    image.id_post = post.id
    db.session.add(image)
    db.session.commit()
    return True

def _remove_image(post):
    images = models.Image.query.filter(models.Image.id_post == post.id)
    i = 1
    for image in images:
        try:
            os.remove(os.path.join(app.config['FILE_UPLOAD_PATH'], "covers", image.filename))
            os.remove(os.path.join(app.config['FILE_UPLOAD_PATH'], "covers", "post_{}_{}.png".format(post.id, i)))
            db.session.delete(image)
        except Exception as e:
            app.logger.error('Error occurred during cover image deletion: %s', e)
            return False
        i += 1
    post.cover_image = 0
    
    db.session.commit()
    return True






def _save_cover_image(data, full_file, post):
    app.logger.debug("Adding cover image to news %s", post.id)
    if data is None or post is None:
        app.logger.error("None is not accepted")
        return False
    filename = secure_filename("ci_{}.png".format(post.id))
    fn, file_extension = os.path.splitext(full_file.filename)
    full_filename = secure_filename("ci_{}_full{}".format(post.id, file_extension))
    try:
        app.logger.debug("Storing images %s and %s to drive", filename, full_filename)
        with open(os.path.join(app.config['FILE_UPLOAD_PATH'], "covers", filename), "wb") as fh:
            fh.write(base64.b64decode(data.split(",")[1]))
        full_file.save(os.path.join(app.config['FILE_UPLOAD_PATH'], "covers", full_filename))
    except Exception as e:
        app.logger.error('Error ocurried during cover image file saving: %s', e)
        return False
    post.cover_image = full_filename
    db.session.commit()
    return True


def _remove_cover_image(post):
    try:
        os.remove(os.path.join(app.config['FILE_UPLOAD_PATH'], "covers", post.cover_image))
        os.remove(os.path.join(app.config['FILE_UPLOAD_PATH'], "covers", "ci_{}.png".format(post.id)))
    except Exception as e:
        app.logger.error('Error occurred during cover image deletion: %s', e)
        return False
    post.cover_image = None
    db.session.commit()
    return True
