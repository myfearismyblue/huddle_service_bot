class BaseVKException(Exception):
    """Base for all VK exceptions"""


class VKBadRequestException(BaseVKException):
    """Raises when vk api responses with error"""


class VKNonRegularPostResponse(BaseVKException):
    """Raises when can't parse milongas inside valid milonga response"""


class NotAppropriateContent(BaseVKException):
    """Raises when can't parse appropriate content inside valid post"""
