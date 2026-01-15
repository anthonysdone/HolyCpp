// Conway's Game of Life in HolyC for TempleOS
// Ported from Rosetta Code. Original C Source:
// - http://rosettacode.org/wiki/Conway's_Game_of_Life#C

#define WIDTH  60
#define HEIGHT 40
#define SLEEP  100

U32 Universe[HEIGHT][WIDTH];
U64 COUNT;

// Show Universe
U0 Show()
{
  U32 x,y;
  // Clear screen using ANSI escape codes
  Print("\033[2J\033[H");
  for (y=0;y<HEIGHT;y++) {
    for (x=0;x<WIDTH;x++) {
      if (Universe[y][x])
        Print("#");
      else
        Print(" ");
    }
    Print("\n");
  }
  Print("\n\nGeneration: %d\n", COUNT);
}

// Update Universe
U0 Evolve()
{
  U32 x,y,y1,x1,n;
  U32 NewUniverse[HEIGHT][WIDTH];

  // Count neighbours
  for (y=0;y<HEIGHT;y++) {
    for (x=0;x<WIDTH;x++) {
      n = 0;

      for (y1=y-1;y1<=y+1;y1++)
        for (x1=x-1;x1<=x+1;x1++)
          if (Universe[(y1+HEIGHT) % HEIGHT][(x1+WIDTH) % WIDTH] > 0)
            n++;

      if (Universe[y][x] > 0)
        n--;

      // Populate new Universe array
      if (n == 3 || (n == 2 && Universe[y][x] > 0))
        NewUniverse[y][x] = 1;
      else
        NewUniverse[y][x] = 0;
    }
  }

  // Update Universe array with new generation
  for (y=0;y<HEIGHT;y++)
    for (x=0;x<WIDTH;x++)
      Universe[y][x] = NewUniverse[y][x];
}

// Seed new Universe
// Each cell has 12.5% chance of life in new Universe
U0 Init()
{
  COUNT = 0;
  U32 x,y;
  for (y=0;y<HEIGHT;y++)
    for (x=0;x<WIDTH;x++)
      if (RandI32 > 0 && RandI32 > 0 && RandI32 > 0)
        Universe[y][x] = 1;
}

U0 Life()
{
  Init;

  Print("\nWelcome to Conway's Game of Life!\n");
  Print("The simulation will run continuously.\n");
  Print("Press Ctrl+C to exit.\n\n");
  Sleep(2000);

  while (TRUE) {
    Show;
    Evolve;
    Sleep(SLEEP);
    COUNT++;
  }
}
Life;