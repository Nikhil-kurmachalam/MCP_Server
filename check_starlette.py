try:
    from starlette.middleware.trustedhost import TrustedHostMiddleware
    print("Starlette middleware found")
except ImportError:
    print("Starlette middleware NOT found")
