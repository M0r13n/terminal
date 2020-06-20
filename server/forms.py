from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired


class DemographyForm(FlaskForm):
    class Meta:
        csrf = False

    age = SelectField(
        validators=[
            DataRequired(),
        ],
        choices=[
            (1, '<18'),
            (2, '18-29'),
            (3, '29-39'),
            (4, '39-59'),
            (5, '59+')
        ],
        coerce=int
    )

    gender = SelectField(
        validators=[
            DataRequired(),
        ],
        choices=[
            (1, 'other'),
            (2, 'female'),
            (3, 'male'),
        ],
        coerce=int
    )

    english_skills = SelectField(
        validators=[
            DataRequired(),
        ],
        choices=[
            (1, 'very good'),
            (2, 'good'),
            (3, 'not so good'),
            (4, 'nonexistent'),
        ],
        coerce=int
    )

    bash_experience = SelectField(
        validators=[
            DataRequired(),
        ],
        choices=[
            (1, 'daily'),
            (2, 'occasionally'),
            (3, 'rarely'),
            (4, 'ery rarely'),
            (5, 'never'),
        ],
        coerce=int
    )

    def get_errors(self):
        errors = [(fieldName, errorMessages) for fieldName, errorMessages in self.errors.items()]
        return errors

    def get_value(self, field):
        field = getattr(self, field)
        return dict(field.choices).get(field.data)

    def populate_user(self, user):
        user.age = self.get_value('age')
        user.gender = self.get_value('gender')
        user.english_skills = self.get_value('english_skills')
        user.bash_experience = self.get_value('bash_experience')
