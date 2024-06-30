import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
        CustomPasswordValidator class to define the custom password validator.

        This class defines the custom password validator to validate the password based on the given criteria.

        Attributes:
            minlength: The minimum length of the password.
            minlower: The minimum number of lowercase letters in the password.
            minupper: The minimum number of uppercase letters in the password.
            minspecial: The minimum number of special characters in the password.
            mindigit: The minimum number of digits in the password.

        Methods:
            validate: Method to validate the password based on the given criteria.
            get_help_text: Method to get the help text for the password validator.
    """
    def __init__(self, minlength=8, minlower=1, minupper=1, minspecial=1, mindigit=1):
        """
            Initialize the custom password validator.
            
            This method initializes the custom password validator with the given criteria.
            
            Args:
                minlength: The minimum length of the password.
                minlower: The minimum number of lowercase letters in the password.
                minupper: The minimum number of uppercase letters in the password.
                minspecial: The minimum number of special characters in the password.
                mindigit: The minimum number of digits in the password.
                
            Returns:
                None
        """
        self.minlength = minlength
        self.minlower = minlower
        self.minupper = minupper
        self.minspecial = minspecial
        self.mindigit = mindigit
        self.special_characters_regex = re.compile(r"[@#!$%]")

    def validate(self, password, user=None):
        """
            Validate the password based on the given criteria.
            
            This method validates the password based on the given criteria.
            
            Args:
                password: The password to validate.
                user: The user object (default=None).
                
            Raises:
                ValidationError: If the password does not meet the criteria.
                
            Returns:
                None
        """
        if len(password) < self.minlength:
            raise ValidationError(
                _("This password must contain at least %(minlength)d characters."),
                code="password_too_short",
                params={"minlength": self.minlength},
            )

        if len(re.findall(r"[a-z]", password)) < self.minlower:
            raise ValidationError(
                _(
                    "This password must contain at least %(minlower)d lowercase letter(s)."
                ),
                code="password_no_lower",
                params={"minlower": self.minlower},
            )

        if len(re.findall(r"[A-Z]", password)) < self.minupper:
            raise ValidationError(
                _(
                    "This password must contain at least %(minupper)d uppercase letter(s)."
                ),
                code="password_no_upper",
                params={"minupper": self.minupper},
            )

        if len(re.findall(r"[0-9]", password)) < self.mindigit:
            raise ValidationError(
                _("This password must contain at least %(mindigit)d digit(s)."),
                code="password_no_digit",
                params={"mindigit": self.mindigit},
            )

        if len(re.findall(self.special_characters_regex, password)) < self.minspecial:
            raise ValidationError(
                _(
                    "This password must contain at least %(minspecial)d special character(s) from @#!$%."
                ),
                code="password_no_special",
                params={"minspecial": self.minspecial},
            )

        if user and user.check_password(password):
            raise ValidationError(
                _("The new password cannot be the same as the old password."),
                code="password_same_as_old",
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
