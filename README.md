# Coach's Coach

A Flask-based web application designed to simplify attendance reporting and student schedule management for job coaches.

## Features

- Generate formatted attendance text by selecting a worksite, weekday, and student initials.
- Copy generated attendance text for use in reporting.
- Maintain worksites, student identifiers, and weekly schedules through a password-protected administration interface.
- Support students who share the same initials.
- Prevent conflicting student schedule assignments through database constraints.

## Technology Stack

- Python
- Flask and Jinja2
- SQLite
- Bootstrap 5
- Flask-WTF for CSRF protection
- Werkzeug for password hashing

## Security

Administrative functionality requires authentication. The application uses password hashing, signed Flask sessions, protected admin routes, and CSRF tokens.

Configuration secrets and the SQLite database are excluded from version control.

## Project Background

Coach's Coach was developed to reduce repetitive attendance-reporting work in a community-based transition program. The application emphasizes a simple, mobile-friendly interface and practical administrative tools.