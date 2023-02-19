class BaseVKException(Exception):
    """Base for all VK exceptions"""


class BadRequestException(BaseVKException):
    """Raises when vk api responses with error"""


class NonRegularMilongaResponse(BaseVKException):
    """Raises when can't parse milongas inside valid milonga response"""
