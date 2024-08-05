from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def __init__(self, minlength=8, minlower=1, minupper=1, minspecial=1, mindigit=1):
        self.minlength = minlength
        self.minlower = minlower
        self.minupper = minupper
        self.minspecial = minspecial
        self.mindigit = mindigit
        self.special_characters = "!@#$%^&*()-_+=[]|;:\"\'<>,.?/"

    def validate(self, password, user=None):
        errors = []

        if len(password) < self.minlength:
            raise ValidationError(
                _("This password must contain at least {minlength} characters.").format(minlength=self.minlength)
            )

        if sum(1 for c in password if c.islower()) < self.minlower:
            raise ValidationError(
                _("This password must contain at least {minlower} lowercase letter(s).").format(minlower=self.minlower)
            )

        if sum(1 for c in password if c.isupper()) < self.minupper:
            raise ValidationError(
                _("This password must contain at least {minupper} uppercase letter(s).").format(minupper=self.minupper)
            )

        if sum(1 for c in password if c.isdigit()) < self.mindigit:
            raise ValidationError(
                _("This password must contain at least {mindigit} digit(s).").format(mindigit=self.mindigit)
            )

        if sum(1 for c in password if c in self.special_characters) < self.minspecial:
            raise ValidationError(
                _("This password must contain at least {minspecial} special character(s) from {specials}.").format(minspecial=self.minspecial, specials=self.special_characters)
            )

        if user and user.check_password(password):
            raise ValidationError(
                _("The new password cannot be the same as the old password.")
            )

    def get_help_text(self):
        """
            Get the help text for the password validator.
            
            This method returns the help text for the password validator.
            
            Returns:
                str: The help text for the password validator.
        """
        return _(
            "Your password must contain at least %(minlength)d characters, "
            "including at least %(minlower)d lowercase letter(s), "
            "%(minupper)d uppercase letter(s), %(mindigit)d digit(s), and "
            "%(minspecial)d special character(s) from @#!$%."
        ) % {
            "minlength": self.minlength,
            "minlower": self.minlower,
            "minupper": self.minupper,
            "mindigit": self.mindigit,
            "minspecial": self.minspecial,
        }
