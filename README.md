# Movie Poster Wall

A beautiful web application that allows you to search for movies and create your own poster wall.

## Quick Start

### Option 1: Double-click to Run (Easiest)
1. Simply double-click the `start_movie_wall.command` file
2. Your default web browser will open to http://localhost:3000 automatically
3. Start searching for movies and building your poster wall!

### Option 2: Terminal
1. Open Terminal
2. Navigate to the application directory:
   ```bash
   cd /Users/quan/CascadeProjects/movie_poster_wall
   ```
3. Run the application:
   ```bash
   python3 app.py
   ```
4. Open your web browser and go to http://localhost:3000

## How to Quit the Application

### If started with double-click:
1. Close the Terminal window that opened with the application
2. Or press Ctrl+C in the Terminal window to stop the server

### If started from Terminal:
1. Press Ctrl+C in the Terminal to stop the server
2. Or type 'exit' to close the Terminal

Note: Just closing the browser window doesn't stop the application. Make sure to stop the server using one of the methods above.

## Features
- Search for any movie and add its poster to your wall
- Zoom in/out with slider or buttons (50% - 200%)
- Keyboard shortcuts: Ctrl/Cmd + Plus/Minus to zoom
- Your posters and zoom level are saved automatically
- Clear all posters with one click
- Beautiful, responsive design

## Troubleshooting
If you get an error about "port already in use":
1. Open Terminal
2. Run: `lsof -i :3000`
3. Find the process ID (PID) using port 3000
4. Run: `kill <PID>` (replace <PID> with the actual number)
5. Try starting the application again

Note: The "WARNING: This is a development server" message is normal and can be safely ignored when running locally.

## Requirements
- Python 3
- Internet connection (for fetching movie posters)

Your poster wall data is automatically saved in your browser and will be there when you return!
