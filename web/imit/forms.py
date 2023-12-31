from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField, PasswordField, HiddenField, TextAreaField, validators, BooleanField


class LoginForm(FlaskForm):
    uid = StringField("Имя пользователя",
                      [validators.InputRequired(message="Обязательно к заполнению"),
                       validators.Length(min=3, max=30)])
    password = PasswordField("Пароль",
                             [validators.InputRequired(message="Обязательно к заполнению"),
                              validators.Length(min=3, max=30)])


class NewsForm(FlaskForm):
    title = StringField("Заголовок",
                        [validators.InputRequired(),
                         validators.Length(min=3, max=256,
                                           message="Необходим текст не более 256 символов и не менее 3")])
    delete_cover_image = BooleanField("", default=False)
    full_cover_image = FileField("Титульное изображение",
                                 [validators.Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'],
                                                                     'Допустимы только файлы изображений!')])
    cropped_cover_image_data = \
        HiddenField("", [validators.Optional(),
                         validators.Regexp(r"^data:image\/png;base64,[A-Za-z0-9!$&',()*+;=\-._~:@\/?%\s]+$")])
    full_text = TextAreaField("Текст", [validators.InputRequired()])
    date = StringField("Дата", [validators.Optional(),
                                validators.Regexp(r"^\d\d\.\d\d\.\d\d\d\d$")])

class MenuForm(FlaskForm):
    link = StringField("Ссылка",
                        [validators.InputRequired(),
                         validators.Length(min=1, max=100,
                                           message="Необходим текст не более 100 символов и не менее 1")])
    name = StringField("Заголовок",
                        [validators.InputRequired(),
                         validators.Length(min=3, max=100,
                                           message="Необходим текст не более 100 символов и не менее 1")])
    is_list = BooleanField("Есть ли подпункты", default=False)


class InitUserForm(FlaskForm):
    uid = StringField("Имя пользователя",
                      [validators.InputRequired(message="Обязательно к заполнению"),
                       validators.Length(min=3, max=30)])


class CreateCustomUserForm(FlaskForm):
    uid = StringField("Имя пользователя",
                      [validators.InputRequired(message="Обязательно к заполнению"),
                       validators.Length(min=3, max=30)])
    password = PasswordField("Пароль",
                             [validators.InputRequired(message="Обязательно к заполнению"),
                              validators.Length(min=6, max=30)])


class PageForm(FlaskForm):
    title_ru = StringField("Заголовок",
                           [validators.InputRequired(),
                            validators.Length(min=3, max=256,
                                              message="Необходим текст не более 256 символов и не менее 3")])
    text_ru = TextAreaField("Текст", default="")
    # title_en = StringField("Заголовок на английском",
    #                       [validators.InputRequired(),
    #                        validators.Length(min=3, max=256,
    #                                          message="Необходим текст не более 256 символов и не менее 3")])
    # text_en = TextAreaField("Текст на английском", default="")
    make_advert = BooleanField("Сделать объявление об изменении", [validators.Optional()])
    advert_text = StringField("Текст объявления",
                              [validators.Optional(),
                               validators.Length(min=0, max=256,
                                                 message="Необходим текст не более 256 символов")])


class FileForm(FlaskForm):
    file = FileField("Файл", [FileRequired()])
    description = StringField("Описание", [validators.InputRequired()])
    post_id = HiddenField("Новость", [validators.Optional()])
    page_id = HiddenField("Страница", [validators.Optional()])


class FileEditForm(FlaskForm):
    file_id = HiddenField("Идентификатор файла", [validators.InputRequired()])
    description = StringField("Описание", [validators.InputRequired()])


class FileRemoveForm(FlaskForm):
    file_id = HiddenField("Идентификатор файла", [validators.InputRequired()])

class FAQFileForm(FlaskForm):
    file = FileField("Файл", [FileRequired(), FileAllowed(['js','json', 'txt'], "Только файлы JSON допустимы.")])

