#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>
#include <array>

using namespace std;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
struct stringbuilder
{
   std::stringstream ss;
   template<typename T>
   stringbuilder & operator << (const T &data)
   {
        ss << data;
        return *this;
   }
   operator std::string() { return ss.str(); }
};

struct Unit
{
    int x;
    int y;
};

struct Cell
{
    int h = 0;
};

typedef std::array<std::array<Cell, 8>, 8> Array;
struct Grid
{
    void newRow(int i, const string& str) {
        int j = 0;
        for (const char& c : str) {
            array[i][j].h = c - '0';
            //cout << array[i][j].h;
            ++j;
        }
    }
    Cell pos(int ind, int offX, int offY) const {
        const Unit& u = units[ind];
        //cerr << u.y << " " << u.x << " " << offY << " " << offX;
        return array[u.y + offY][u.x + offX];
    }
    int possibleMoves(int x, int y, int bx, int by) const {
        int m = 0;
        int hm = array[y][x].h;
        for (int i = -1; i <= 1; i += 2) {
            for (int j = -1; j <= 1; j += 2) {
                int h = array[y+j][x+i].h;
                if (bx == i && by == j)
                    ++h;
                if (h >= 0 && h <= hm) {
                    ++m;
                }
                for (const Unit& u : units) {
                    if (x+i == u.x && y+j == u.y)
                        --m;
                }
                for (const Unit& u : other) {
                    if (x+i == u.x && y+j == u.y)
                        --m;
                }
            }
        }
        //cerr << x<<y<<bx<<by<<m;
        return m;
    }
    
    int size = 0;
    Array array;
    vector<Unit> units;
    vector<Unit> other;
};

struct Action
{
    void fromInput(const string& theType, int index, const string& thedir1, const string& thedir2) {
        ind = index;
        type = theType;
        dir1 = thedir1;
        dir2 = thedir2;
        mv = bd = 5;
        mvX = mvY = bdX = bdY = 0;
        for (const char& c: dir1) {
            switch(c) {
                case 'N':
                    mvY -=1;
                    mv += 3;
                    break;
                case 'S':
                    mvY +=1;
                    mv += -3;
                    break;
                case 'E':
                    mvX +=1;
                    mv += 1;
                    break;
                case 'W':
                    mvX -=1;
                    mv += -1;
                    break;
            }
        }
        for (const char& c: dir2) {
            switch(c) {
                case 'N':
                    bdY -=1;
                    bd += 3;
                    break;
                case 'S':
                    bdY +=1;
                    bd += -3;
                    break;
                case 'E':
                    bdX +=1;
                    bd += 1;
                    break;
                case 'W':
                    bdX -=1;
                    bd += -1;
                    break;
            }
        }
        //cerr <<ind<<" "<<dir1<<" "<<dir2<<" "<<mvX<<" "<<mvY<<endl;
    }
    string str() const {
        return stringbuilder() << type << " " << ind << " " << dir1 << " " << dir2;
    }
    
    
    double expectedPoints(const Grid& grid) const {
        int offX = mvX;
        int offY = mvY;
        double h = grid.pos(ind, 0, 0).h;
        double hi = h;
        double m = 0;
        double du = 0;
        if (type == "PUSH&BUILD") {
            offX = offY = 0;
            h = 3*grid.pos(ind, mvX, mvY).h;
            h -= grid.pos(ind, 2*mvX, 2*mvY).h;
        }
        if (type == "MOVE&BUILD") {
            h += grid.pos(ind, offX, offY).h;
            m = grid.possibleMoves(grid.units[ind].x + mvX, grid.units[ind].y + mvY, bdX, bdY);
        }
        double bi = grid.pos(ind, offX+bdX, offY+bdY).h;
        double b = -abs(hi - bi)*0.2;
        if (bi == 3)
            b -= 0.7;
//        else
//            b = 0.5;
        return h + b + m*0.1;
    }
    string dir1, dir2;
    int ind;
    string type;
    int mvX,mvY,bdX,bdY;
    int mv;
    int bd;
};

int main()
{
    Grid grid;
    cin >> grid.size; cin.ignore();
    int unitsPerPlayer;
    cin >> unitsPerPlayer; cin.ignore();
    for (int i = 0; i < unitsPerPlayer; i++) {
        grid.units.push_back(Unit());
        grid.other.push_back(Unit());
    }
    // game loop
    while (1) {
        vector<Action> actions;
        for (int i = 0; i < grid.size; i++) {
            string row;
            cin >> row; cin.ignore();
            grid.newRow(i, row);
        }
        for (int i = 0; i < unitsPerPlayer; i++) {
            cin >> grid.units[i].x >> grid.units[i].y; cin.ignore();
        }
        for (int i = 0; i < unitsPerPlayer; i++) {
            cin >> grid.other[i].x >> grid.other[i].y; cin.ignore();
        }
        int legalActions;
        cin >> legalActions; cin.ignore();
        for (int i = 0; i < legalActions; i++) {
            string atype;
            int index;
            string dir1;
            string dir2;
            cin >> atype >> index >> dir1 >> dir2; cin.ignore();
            Action a;
            a.fromInput(atype, index, dir1, dir2);
            actions.push_back(a);
        }
        //cout << endl;

        // Write an action using cout. DON'T FORGET THE "<< endl"
        // To debug: cerr << "Debug messages..." << endl;
        std::sort(actions.begin(), actions.end(), [&](const Action& a,const Action& b){
            return a.expectedPoints(grid) > b.expectedPoints(grid);
            });
        Action a = actions[0];
        cout << actions[0].str() << endl;
    }
}