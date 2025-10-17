def test_import_and_version():
    import ares
    assert hasattr(ares, "__version__")
