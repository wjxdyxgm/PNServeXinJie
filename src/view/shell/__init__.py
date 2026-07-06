from .page_stack import DashboardPageStack
from .footer_feedback import build_footer_feedback
from .footer_bar import FooterBar
from .header_bar import HeaderBar
from .operator_login import request_operator_name
from .window_chrome import apply_dashboard_style, create_window_shadow

__all__ = [
    "DashboardPageStack",
    "FooterBar",
    "HeaderBar",
    "apply_dashboard_style",
    "build_footer_feedback",
    "create_window_shadow",
    "request_operator_name",
]
