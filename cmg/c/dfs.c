/* Step-budget DFS for counter clip setups. A setup is (turn, move)* + final turn; its step count is
   the sum of turn/move costs (tap 1, ESS group 1, each spin in place 1, each guano scoot 1, other moves 1).
   Enumerates every setup with at most BUDGET steps (and at most MAXESS ESS groups) and prints
   candidates whose approximate clip-frame position falls in an exodus Yes box.
   usage: dfs DIR BUDGET MAXESS x0 z0 a0 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>
typedef struct { double dx, dz; uint16_t mode, ff; uint8_t valid; } MoveB;
typedef struct { double cx, cz, sw, cw, s8, c8, x0, x1, z0, z1; } Ray;
static int NT, NM, NR, BUDGET, MAXESS;
static uint16_t *turns; static MoveB *moves; static int16_t *finals; static Ray *rays;
static int32_t *movekind, *turnkind, *tcost, *mcost, *tess;
static void *slurp(const char *dir, const char *name, long *n) {
    char p[512]; snprintf(p, sizeof p, "%s/%s", dir, name);
    FILE *f = fopen(p, "rb"); if (!f) { perror(p); exit(1); }
    fseek(f, 0, SEEK_END); *n = ftell(f); fseek(f, 0, SEEK_SET);
    void *b = malloc(*n); if (fread(b, 1, *n, f) != (size_t)*n) exit(2); fclose(f); return b;
}
static int valid(double x, double z) { return x > -420 && x < 66 && z > 134 && z < 797; }
static int inside(double x, double z, double m) { return x > -1680 + m && x < 80 - m && z > 120 + m && z < 811 - m; }
static FILE *out; static long nhits;
typedef struct { double x, z; uint16_t a; } S;
static int apply(const S *s, int t, int m, S *o) {
    uint16_t a2 = turns[(size_t)t * 65536 + s->a];
    if (turnkind[t] & 1) { double ang = s->a * (2 * M_PI / 65536.0); if (!inside(s->x - 70 * sin(ang), s->z - 70 * cos(ang), 15)) return 0; }
    const MoveB *mb = &moves[(size_t)m * 4096 + (a2 >> 4)];
    if (!mb->valid) return 0;
    double x, z;
    if (movekind[m] == 1) { x = 66; z = 134; }
    else if (movekind[m] == 2) { x = s->x; z = 134; if (!((x > -346 && x < -114) || (x > -26 && x < 66))) return 0; }
    else { x = s->x + mb->dx; z = s->z + mb->dz;
           if (movekind[m] == 3 && !(inside(s->x, s->z, 100) && inside(x, z, 100) && s->x > -320 && x > -320)) return 0; }
    if (!valid(x, z)) return 0;
    o->x = x; o->z = z; o->a = mb->mode ? mb->ff : a2; return 1;
}
static void final_check(const S *s, int rem, int essleft, const int *path, int np) {
    const int16_t *fl = &finals[(size_t)s->a * 16];
    for (int k = 0; k < 8 && fl[2 * k] >= 0; k++) {
        int ft = fl[2 * k];
        if (tcost[ft] > rem || (tess[ft] && essleft <= 0)) continue;
        const Ray *r = &rays[fl[2 * k + 1]];
        double dx = r->cx - s->x - 12 * r->s8, dz = r->cz - s->z - 12 * r->c8;
        double e = rint(((dx * r->sw + dz * r->cw) / 1.5 - 18) / 6);
        if (e < 0 || e > 75) continue;
        double qx = s->x + 1.5 * (18 + 6 * e) * r->sw + 12 * r->s8, qz = s->z + 1.5 * (18 + 6 * e) * r->cw + 12 * r->c8;
        if (qx > r->x0 - 0.004 && qx < r->x1 + 0.004 && qz > r->z0 - 0.04 && qz < r->z1 + 0.04) {
            #pragma omp critical
            { for (int i = 0; i < np; i++) fprintf(out, "%d,%d ", path[2 * i], path[2 * i + 1]);
              fprintf(out, "| %d %d\n", ft, BUDGET - rem + tcost[ft]); nhits++; }
        }
    }
}
static void dfs(const S *s, int rem, int essleft, int *path, int np) {
    final_check(s, rem, essleft, path, np);
    for (int t = 0; t < NT; t++) {
        if (tcost[t] > rem - 1) continue;
        if (tess[t] && essleft <= 0) continue;
        for (int m = 0; m < NM; m++) {
            if (tcost[t] + mcost[m] > rem) continue;
            S o; if (!apply(s, t, m, &o)) continue;
            path[2 * np] = t; path[2 * np + 1] = m;
            dfs(&o, rem - tcost[t] - mcost[m], essleft - tess[t], path, np + 1);
        }
    }
}
int main(int argc, char **argv) {
    const char *dir = argv[1]; BUDGET = atoi(argv[2]); MAXESS = atoi(argv[3]);
    long n;
    turns = slurp(dir, "turns.bin", &n); NT = n / (65536 * 2);
    char *mb = slurp(dir, "moves.bin", &n); long rec = 21; NM = n / (rec * 4096);
    moves = malloc(sizeof(MoveB) * NM * 4096);
    for (long i = 0; i < (long)NM * 4096; i++) { char *p = mb + i * rec; memcpy(&moves[i].dx, p, 8); memcpy(&moves[i].dz, p + 8, 8);
        memcpy(&moves[i].mode, p + 16, 2); memcpy(&moves[i].ff, p + 18, 2); moves[i].valid = p[20]; }
    movekind = slurp(dir, "movekind.bin", &n); turnkind = slurp(dir, "turnkind.bin", &n);
    tcost = slurp(dir, "turncost.bin", &n); mcost = slurp(dir, "movecost.bin", &n); tess = slurp(dir, "turness.bin", &n);
    finals = slurp(dir, "final.bin", &n); rays = slurp(dir, "rays.bin", &n); NR = n / sizeof(Ray);
    char op[512]; snprintf(op, sizeof op, "%s/dfs_hits_%d.txt", dir, BUDGET); out = fopen(op, "w");
    S s0 = { atof(argv[4]), atof(argv[5]), (uint16_t)atoi(argv[6]) };
    final_check(&s0, BUDGET, MAXESS, NULL, 0);
    /* parallelise over the first (turn, move) */
    int first[200000][2]; int nf = 0;
    for (int t = 0; t < NT; t++) for (int m = 0; m < NM; m++) if (tcost[t] + mcost[m] <= BUDGET) { first[nf][0] = t; first[nf][1] = m; nf++; }
    long done = 0;
    #pragma omp parallel for schedule(dynamic, 1)
    for (int i = 0; i < nf; i++) {
        int t = first[i][0], m = first[i][1];
        if (tess[t] && MAXESS <= 0) continue;
        S o; if (!apply(&s0, t, m, &o)) continue;
        int path[64]; path[0] = t; path[1] = m;
        dfs(&o, BUDGET - tcost[t] - mcost[m], MAXESS - tess[t], path, 1);
        #pragma omp atomic
        done++;
    }
    fprintf(stderr, "budget %d: candidates %ld\n", BUDGET, nhits);
    fclose(out); return 0;
}
