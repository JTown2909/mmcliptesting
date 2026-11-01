/* Exhaustive (turn, move)^depth search for chest-minigame counter clip setups.
   Approximate float64 positions (prefilter); candidates are re-checked exactly in Python.
   Inputs (written by prep.py into DIR):
     turns.bin   uint16 [NT][65536]   facing after turn t
     moves.bin   per move m, per bin b: double dx, dz; uint16 finalmode(0=keep,1=table) ; uint16 ffacing; uint8 valid
     final.bin   per facing f: up to 8 (turn idx int16, ray idx int16), -1 terminated
     rays.bin    per ray r: double cx, cz, sw, cw, s8, c8, x0, x1, z0, z1
   argv: DIR depth x0 z0 a0 maxturn_levels... */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>

typedef struct { double dx, dz; uint16_t mode, ff; uint8_t valid; } MoveB;
typedef struct { double cx, cz, sw, cw, s8, c8, x0, x1, z0, z1; } Ray;
static int NT, NM, NR;
static uint16_t *turns;           /* NT*65536 */
static MoveB *moves;               /* NM*4096 */
static int16_t *finals;            /* 65536*16 */
static Ray *rays;
static int *movekind;              /* 0 = displacement, 1 = corner pin, 2 = back-wall pin */
static int allowT[8][512];

static void *slurp(const char *dir, const char *name, long *n) {
    char p[512]; snprintf(p, sizeof p, "%s/%s", dir, name);
    FILE *f = fopen(p, "rb"); if (!f) { perror(p); exit(1); }
    fseek(f, 0, SEEK_END); *n = ftell(f); fseek(f, 0, SEEK_SET);
    void *b = malloc(*n); if (fread(b, 1, *n, f) != (size_t)*n) exit(2); fclose(f); return b;
}
typedef struct { double x, z; uint16_t a; int32_t par; int16_t t, m; } St;

static int valid(double x, double z) { return x > -420 && x < 66 && z > 134 && z < 797; }
static int inside(double x, double z, double m) { return x > -1680 + m && x < 80 - m && z > 120 + m && z < 811 - m; }
static int32_t *turnkind;  /* 1 = starts with a tap turn (needs the settled camera clear of walls) */

static inline int apply(const St *s, int t, int m, St *o) {
    uint16_t a2 = turns[(size_t)t * 65536 + s->a];
    if (turnkind[t]) {
        double ang = s->a * (2 * M_PI / 65536.0);
        if (!inside(s->x - 70 * sin(ang), s->z - 70 * cos(ang), 15)) return 0;
    }
    const MoveB *mb = &moves[(size_t)m * 4096 + (a2 >> 4)];
    if (!mb->valid) return 0;
    double x, z;
    if (movekind[m] == 1) { x = 66; z = 134; }
    else if (movekind[m] == 2) { x = s->x; z = 134; if (!((x > -346 && x < -114) || (x > -26 && x < 66))) return 0; }
    else {
        x = s->x + mb->dx; z = s->z + mb->dz;
        if (movekind[m] == 3 && !(inside(s->x, s->z, 100) && inside(x, z, 100) && s->x > -320 && x > -320)) return 0;
    }
    if (!valid(x, z)) return 0;
    o->x = x; o->z = z; o->a = mb->mode ? mb->ff : a2; o->t = t; o->m = m; return 1;
}
static FILE *out;
static long nhits;
static void final_check(const St *s, int level, long idx) {
    const int16_t *fl = &finals[(size_t)s->a * 16];
    for (int k = 0; k < 8 && fl[2 * k] >= 0; k++) {
        const Ray *r = &rays[fl[2 * k + 1]];
        double dx = r->cx - s->x - 12 * r->s8, dz = r->cz - s->z - 12 * r->c8;
        double t = dx * r->sw + dz * r->cw;
        double e = rint((t / 1.5 - 18) / 6);
        if (e < 0 || e > 75) continue;
        double qx = s->x + 1.5 * (18 + 6 * e) * r->sw + 12 * r->s8, qz = s->z + 1.5 * (18 + 6 * e) * r->cw + 12 * r->c8;
        if (qx > r->x0 - 0.004 && qx < r->x1 + 0.004 && qz > r->z0 - 0.04 && qz < r->z1 + 0.04) {
            #pragma omp critical
            { fprintf(out, "%d %ld %d %d %d %d %.6f %.6f %d\n", level, idx, s->par, s->t, s->m, fl[2 * k], s->x, s->z, (int)e); nhits++; }
        }
    }
}
int main(int argc, char **argv) {
    const char *dir = argv[1]; int depth = atoi(argv[2]);
    long n;
    turns = slurp(dir, "turns.bin", &n); NT = n / (65536 * 2);
    char *mb = slurp(dir, "moves.bin", &n);
    long rec = 8 + 8 + 2 + 2 + 1; NM = n / (rec * 4096);
    moves = malloc(sizeof(MoveB) * NM * 4096);
    for (long i = 0; i < (long)NM * 4096; i++) {
        char *p = mb + i * rec; memcpy(&moves[i].dx, p, 8); memcpy(&moves[i].dz, p + 8, 8);
        memcpy(&moves[i].mode, p + 16, 2); memcpy(&moves[i].ff, p + 18, 2); moves[i].valid = p[20];
    }
    long nk; int32_t *mk = slurp(dir, "movekind.bin", &nk); movekind = mk;
    turnkind = slurp(dir, "turnkind.bin", &nk);
    finals = slurp(dir, "final.bin", &n);
    rays = slurp(dir, "rays.bin", &n); NR = n / sizeof(Ray);
    /* allowed turns per level: argv[6+level] = file of allowed turn indices, or "all" */
    for (int L = 0; L < 8; L++) for (int t = 0; t < 512; t++) allowT[L][t] = 1;
    for (int L = 0; L < depth && 6 + L < argc; L++) if (strcmp(argv[6 + L], "all")) {
        for (int t = 0; t < 512; t++) allowT[L][t] = 0;
        char *s = strdup(argv[6 + L]), *tok = strtok(s, ",");
        while (tok) { allowT[L][atoi(tok)] = 1; tok = strtok(NULL, ","); }
    }
    char op[512]; snprintf(op, sizeof op, "%s/hits.txt", dir); out = fopen(op, "w");
    fprintf(stderr, "NT=%d NM=%d NR=%d\n", NT, NM, NR);
    St *cur = malloc(sizeof(St)); cur[0].x = atof(argv[3]); cur[0].z = atof(argv[4]); cur[0].a = atoi(argv[5]);
    cur[0].par = -1; cur[0].t = -1; cur[0].m = -1;
    long ncur = 1;
    for (int L = 0; L < depth; L++) {
        char sp[512]; snprintf(sp, sizeof sp, "%s/level%d.bin", dir, L);
        FILE *f = fopen(sp, "wb"); fwrite(cur, sizeof(St), ncur, f); fclose(f);
        final_check(&cur[0], L, 0);
        for (long i = 1; i < ncur; i++) final_check(&cur[i], L, i);
        if (L == depth - 2 && depth >= 4) {
            /* stream the last two levels: per stored state, children c3, then only (t,m) whose
               resulting facing has a final turn (precomputed per facing) */
            typedef struct { int16_t t; int8_t m; uint16_t ff; } E;
            static E *lst; static int *off;
            off = malloc(sizeof(int) * 65537); long tot = 0;
            for (int pass = 0; pass < 2; pass++) {
                tot = 0;
                for (int a = 0; a < 65536; a++) {
                    off[a] = tot;
                    for (int t = 0; t < NT; t++) if (allowT[L + 1][t]) for (int m = 0; m < NM; m++) {
                        if (movekind[m] == 1) continue;
                        uint16_t a2 = turns[(size_t)t * 65536 + a];
                        const MoveB *mb = &moves[(size_t)m * 4096 + (a2 >> 4)];
                        if (!mb->valid) continue;
                        uint16_t ff = mb->mode ? mb->ff : a2;
                        if (finals[(size_t)ff * 16] < 0) continue;
                        if (pass) { lst[tot].t = t; lst[tot].m = m; lst[tot].ff = ff; }
                        tot++;
                    }
                }
                off[65536] = tot;
                if (!pass) lst = malloc(sizeof(E) * tot);
            }
            fprintf(stderr, "last-move lists: %ld entries (%.1f per facing)\n", tot, tot / 65536.0);
            long done = 0;
            #pragma omp parallel for schedule(dynamic, 16)
            for (long i = 0; i < ncur; i++) {
                St c3, c4;
                for (int t = 0; t < NT; t++) if (allowT[L][t]) for (int m = 0; m < NM; m++) {
                    if (!apply(&cur[i], t, m, &c3)) continue;
                    if (c3.x < -420 || c3.x > 66) continue;
                    for (int k = off[c3.a]; k < off[c3.a + 1]; k++) {
                        if (!apply(&c3, lst[k].t, lst[k].m, &c4)) continue;
                        if (c4.x < -246 || c4.x > -212) continue;
                        c4.par = i; c4.t = t * 64 + m; c4.m = lst[k].t * 64 + lst[k].m;
                        final_check(&c4, L + 2, -2);
                    }
                }
                #pragma omp atomic
                done++;
                if (done % 20000 == 0) fprintf(stderr, "  %ld / %ld\n", done, ncur);
            }
            break;
        }
        if (L == depth - 1) {
            /* last level: stream children through the final check without storing them */
            #pragma omp parallel for schedule(dynamic, 64)
            for (long i = 0; i < ncur; i++) {
                St o;
                for (int t = 0; t < NT; t++) if (allowT[L][t]) for (int m = 0; m < NM; m++)
                    if (apply(&cur[i], t, m, &o)) { o.par = i; final_check(&o, L + 1, -1); }
            }
            break;
        }
        long cap = ncur * 64 + 1024, nn = 0;
        St *nxt = malloc(sizeof(St) * cap);
        for (long i = 0; i < ncur; i++)
            for (int t = 0; t < NT; t++) if (allowT[L][t]) for (int m = 0; m < NM; m++) {
                St o; if (!apply(&cur[i], t, m, &o)) continue;
                o.par = i;
                if (nn == cap) { cap *= 2; nxt = realloc(nxt, sizeof(St) * cap); }
                nxt[nn++] = o;
            }
        /* dedup by (quantised x, z, facing) */
        typedef struct { int64_t k1, k2; long i; } K;
        K *ks = malloc(sizeof(K) * nn);
        for (long i = 0; i < nn; i++) { ks[i].k1 = llrint(nxt[i].x * 1e5) * 65536 + nxt[i].a; ks[i].k2 = llrint(nxt[i].z * 1e5); ks[i].i = i; }
        int cmp(const void *A, const void *B) { const K *a = A, *b = B; if (a->k1 != b->k1) return a->k1 < b->k1 ? -1 : 1; if (a->k2 != b->k2) return a->k2 < b->k2 ? -1 : 1; return a->i < b->i ? -1 : a->i > b->i; }
        qsort(ks, nn, sizeof(K), cmp);
        St *ded = malloc(sizeof(St) * nn); long nd = 0;
        for (long i = 0; i < nn; i++) if (i == 0 || ks[i].k1 != ks[i - 1].k1 || ks[i].k2 != ks[i - 1].k2) ded[nd++] = nxt[ks[i].i];
        free(ks); free(nxt); free(cur); cur = ded; ncur = nd;
        fprintf(stderr, "level %d: %ld states (%ld before dedup), hits so far %ld\n", L + 1, nd, nn, nhits);
    }
    fprintf(stderr, "done, candidates %ld\n", nhits);
    fclose(out); return 0;
}
