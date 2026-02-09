from app import create_app


def test_routes_no_server_error():
    app = create_app()
    client = app.test_client()
    routes = [
        '/',
        '/resume/dashboard',
        '/resume/upload',
        '/resume/view',
        '/resume/rewrite',
        '/skills/',
        '/skills/dashboard',
        '/learning/',
        '/learning/dashboard',
        '/jobs/',
        '/jobs/dashboard',
        '/mentors/',
        '/mentors/discover',
        '/admin/dashboard',
        '/admin/users',
    ]

    for r in routes:
        resp = client.get(r)
        assert resp.status_code < 500, f"Route {r} returned {resp.status_code}" 
