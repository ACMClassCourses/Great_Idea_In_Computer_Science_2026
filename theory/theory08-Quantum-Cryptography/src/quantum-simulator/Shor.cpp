// Code by juju527.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef complex<double> C;
typedef vector<C> vec;
typedef vector<vec> Matrix;
#define eb emplace_back
mt19937_64 rnd(random_device{}());
const Matrix X = {{0, 1}, {1, 0}};
const Matrix H = {{1 / sqrt(2), 1 / sqrt(2)}, {1 / sqrt(2), -1 / sqrt(2)}};
Matrix phase(double theta) { return {{1, 0}, {0, exp(C(0, theta))}}; }
struct Qubits {
  int n;
  vec a;
  Qubits(int m) {
    n = m;
    a.resize(1 << m, 0);
    a[0] = 1;
  }
  void apply_gate(Matrix T, int p) {
    int S = (1 << n) - 1;
    vec b(S + 1);
    for (int s = 0; s <= S; s++) {
      int c = (s >> p) & 1;
      for (int d = 0; d < 2; d++)
        b[s ^ ((c ^ d) << p)] += T[d][c] * a[s];
    }
    a = b;
  }
  void apply_cnot(int con, int tar) {
    int S = (1 << n) - 1;
    vec b(S + 1);
    for (int s = 0; s <= S; s++) {
      int c = (s >> con) & 1;
      b[s ^ (c << tar)] += a[s];
    }
    a = b;
  }
  int measure(int p) {
    int S = (1 << n) - 1;
    double pro[2] = {0, 0};
    for (int s = 0; s <= S; s++)
      pro[(s >> p) & 1] += norm(a[s]);
    uniform_real_distribution<double> dist(0.0, 1.0);
    int d = dist(rnd) < pro[1];
    vec b(S + 1);
    double coef = sqrt(pro[d]);
    for (int s = 0; s <= S; s++) {
      int c = (s >> p) & 1;
      if (c ^ d)
        b[s] = 0;
      else
        b[s] = a[s] / coef;
    }
    a = b;
    return d;
  }
};
ll power(ll x, ll b, ll n) {
  ll res = 1;
  while (b) {
    if (b & 1)
      res = (__int128)x * x % n;
    x = (__int128)x * x % n;
    b >>= 1;
  }
  return res;
}
void mul(Qubits &st, int con, ll a, ll N) {
  ll v = power(a, 1ll << con, N);
  int n = st.n / 3, m = n * 2, S = (1 << (n * 3)) - 1;
  vec b(S + 1);
  for (int s = 0; s <= S; s++) {
    if (!((s >> con) & 1)) {
      b[s] += st.a[s];
      continue;
    }
    ll w = (__int128)(s >> m) * v % N;
    b[w << m | (s & ((1ll << m) - 1))] += st.a[s];
  }
  st.a = b;
  return;
}
const int maxs = (1 << 21) + 5;
const double eps = 1e-9, pai = acos(-1.0);
int rev[maxs];
C buf[maxs];
void QFT(Qubits &st, int m, int t) {
  int lim = (1 << m);
  for (int i = 0; i < lim; i++)
    buf[i] = st.a[i | (t << m)];
  for (int i = 0; i < lim; i++)
    if (i < rev[i])
      swap(buf[i], buf[rev[i]]);
  for (int mid = 1; mid < lim; mid <<= 1) {
    C w(cos(pai / mid), sin(pai / mid));
    for (int j = 0; j < lim; j += (mid << 1)) {
      C p(1, 0);
      for (int k = 0; k < mid; k++, p *= w) {
        C u = buf[j + k], v = buf[j + k + mid];
        buf[j + k] = u + v, buf[j + k + mid] = u - v;
      }
    }
  }
  double pr = 0;
  for (int i = 0; i < lim; i++)
    pr += norm(buf[i]);
  for (int i = 0; i < lim; i++)
    st.a[i | (t << m)] = buf[i] / pr;
  return;
}
ll shor_quantum_part(ll a, ll N) {
  for (int T = 1; T <= 10; T++) {
    int n = 0, m = 0;
    while ((1ll << n) < N)
      n++;
    m = 2 * n;
    Qubits st(m + n);
    for (int i = 0; i < m; i++)
      st.apply_gate(H, i);
    st.apply_gate(X, m);
    for (int i = 0; i < m; i++)
      mul(st, i, a, N);
    ll t = 0;
    for (int i = m; i < m + n; i++)
      t |= (st.measure(i) << (i - m));
    for (int i = 1; i < (1 << m); i++)
      rev[i] = rev[i >> 1] | ((i & 1) << (m - 1));
    QFT(st, m, t);
    ll aux = 0;
    for (int i = 0; i < m; i++)
      aux |= (st.measure(i) << i);
    // cerr<<aux<<" "<<(1<<m)<<endl;
    ll p = aux, q = (1 << m);
    vector<ll> frac(0);
    while (q) {
      ll x = p / q, y = 1, tmp = p;
      frac.eb(x);
      for (int i = frac.size() - 2; i >= 0; i--)
        y += frac[i] * x, swap(x, y);
      if (x >= N)
        break;
      if (x && power(a, x, N) == 1)
        return x;
      p = q, q = tmp % q;
    }
  }
  return 0;
}
ll factor(ll n) { // factorize n=p*q
  ll a, g, r;
  do {
    a = rnd() % (n - 1) + 1, g = __gcd(n, a);
    if (g > 1) {
      printf("%lld %lld\n", g, n / g);
      exit(0);
    }
    r = shor_quantum_part(a, n);
  } while (!r || (r & 1));
  ll x = __gcd(power(a, r / 2 - 1, n), n);
  if (x > 1) {
    printf("%lld %lld\n", x, n / x);
    exit(0);
  }
  x = __gcd(power(a, r / 2 + 1, n), n);
  printf("%lld %lld\n", x, n / x);
  exit(0);
}
int main() {
  int n;
  scanf("%d", &n);
  factor(n);
  return 0;
}
