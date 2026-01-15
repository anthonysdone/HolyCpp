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
  DocClear;
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
  CMenuEntry *tempse;

  MenuPush(
    "File {"
    "  Abort(,CH_SHIFT_ESC);"
    "  Exit(,CH_ESC);"
    "}"
    "Play {"
    "  Restart(,'\n');"
    "}"
  );
 
  SettingsPush; // See $LK,"SettingsPush",A="MN:SettingsPush"$
  Fs->text_attr=BLACK<<4+LTGRAY;
  WinMax;
  WinBorder;
  AutoComplete;
  Preempt;
  Init;

  DocClear;
  Fs->draw_it=&DrawIt;
  Fs->win_inhibit=WIG_TASK_DFT-WIF_SELF_FOCUS
    -WIF_SELF_BORDER-WIF_FOCUS_TASK_MENU;

  PopUpOk("
  Welcome to Conway's Game of Life!\n
  Press ENTER to restart");

  try {
    while (TRUE) {
      switch (ScanChar) {
        case CH_ESC:
        case CH_SHIFT_ESC:
          goto wg_done;
        case '\n':
          Init;
          break;
      }
      Show;
      Evolve;
      Sleep(SLEEP);
      COUNT++;
    }
wg_done:
  } catch {
    PutExcept;
  }
  SettingsPop;
  MenuPop;
}
Life;