# Seeding Categories

This document describes how to seed the database with initial event categories.

## Overview

The MeetHub application uses a `Category` model to classify events. Before creating events, you need to have categories available in the database. A Django management command is provided to seed the database with the default categories.

## Available Categories

The following categories are seeded by default:

- **music** - Music events including concerts, festivals, and performances
- **show** - Shows including theater, comedy, and entertainment performances
- **viewing** - Viewing events including movie screenings, exhibitions, and presentations

## Usage

To seed the categories, run the following command from the project root:

```bash
uv run python manage.py seed_categories
```

Or if using a virtual environment:

```bash
python manage.py seed_categories
```

## Command Behavior

The command uses `get_or_create()` to ensure that:
- If a category doesn't exist, it will be created
- If a category already exists, it will be skipped (no duplicate entries)

The command will output:
- Green text for newly created categories
- Yellow text for categories that already exist
- A success message when complete

## Example Output

```
Created category: music
Created category: show
Created category: viewing
Categories seeded successfully!
```

## Adding New Categories

To add new categories, you have two options:

### Option 1: Modify the Command

Edit `meethub/events/management/commands/seed_categories.py` and add new categories to the `categories` list:

```python
categories = [
    {
        'name': 'music',
        'description': 'Music events including concerts, festivals, and performances'
    },
    {
        'name': 'show',
        'description': 'Shows including theater, comedy, and entertainment performances'
    },
    {
        'name': 'viewing',
        'description': 'Viewing events including movie screenings, exhibitions, and presentations'
    },
    {
        'name': 'sports',
        'description': 'Sports events and competitions'
    },
]
```

Then run the command again to seed the new categories.

### Option 2: Use Django Admin

1. Run the development server: `uv run python manage.py runserver`
2. Navigate to `http://127.0.0.1:8000/admin`
3. Log in with your superuser account
4. Go to "Events" → "Categories"
5. Add new categories manually

## Category Model

The `Category` model is defined in `meethub/events/models.py`:

```python
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
```

## Seeding Events

A separate management command is available to seed the database with sample events around coordinates 44.000000, -71.500000 (New Hampshire/Vermont area).

### Usage

To seed events, run:

```bash
uv run python manage.py seed_events
```

Or if using a virtual environment:

```bash
python manage.py seed_events
```

### Command Behavior

The command will:
- Create a test user (test@example.com) if it doesn't exist
- Generate 12 sample events with coordinates within ~0.1 degrees of the center point
- Distribute events across available categories
- Set realistic dates, times, venues, and descriptions
- Use `get_or_create()` to avoid duplicates

### Requirements

The `seed_events` command requires categories to exist first. Run `seed_categories` before running `seed_events`.

### Example Output

```
Test user already exists: test@example.com
Created event: Mountain Music Festival at (44.052345, -71.487654)
Created event: Art Gallery Opening at (43.987654, -71.523456)
...
Seeding complete! Created 12 new events, skipped 0 existing events.
```

## Troubleshooting

### Command Not Found

If you get a "Command not found" error, ensure that:
- The `management` and `commands` directories exist in the events app
- Both directories contain an `__init__.py` file
- The events app is included in `INSTALLED_APPS` in `config/settings.py`

### Permission Denied

If you get a permission error, ensure you have write access to the database file (`db.sqlite3`).

### Categories Already Exist

The command is idempotent - running it multiple times will not create duplicates. Existing categories will be skipped.
