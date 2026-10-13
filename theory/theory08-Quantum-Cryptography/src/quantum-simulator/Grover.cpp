//Code by juju527.
#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef double db;
typedef complex<db> C;
typedef vector<C> vec;
typedef vector<vec> Matrix;
#define eb emplace_back
const db pai=acos(-1.0);
mt19937_64 rnd(233);
const Matrix X={{0, 1},{1, 0}};
const Matrix H={{1/sqrt(2),1/sqrt(2)},{1/sqrt(2),-1/sqrt(2)}};
Matrix phase(double theta){return{{1, 0},{0, exp(C(0, theta))}};}
struct Qubits{
    int n;
    vec a;
    Qubits(int m){
        n=m;
        a.resize(1<<m,0);
        a[0]=1;
    }
    void apply_gate(Matrix T,int p){
        int S=(1<<n)-1;
        vec b(S+1);
        for(int s=0;s<=S;s++){
            int c=(s>>p)&1;
            for(int d=0;d<2;d++)b[s^((c^d)<<p)]+=T[d][c]*a[s];
        }
        a=b;
    }
    void apply_cnot(int con,int tar){
        int S=(1<<n)-1;
        vec b(S+1);
        for(int s=0;s<=S;s++){
            int c=(s>>con)&1;
            b[s^(c<<tar)]+=a[s];
        }
        a=b;
    }
    int measure(int p){
        int S=(1<<n)-1;
        double pro[2]={0,0};
        for(int s=0;s<=S;s++)pro[(s>>p)&1]+=norm(a[s]);
        uniform_real_distribution<double> dist(0.0,1.0);
        int d=dist(rnd)<pro[1];
        vec b(S+1);
        double coef=sqrt(pro[d]);
        for(int s=0;s<=S;s++){
            int c=(s>>p)&1;
            if(c^d)b[s]=0;
            else b[s]=a[s]/coef;
        }
        a=b;
        return d;
    }
    int measure(){
        int ans=0;
        for(int i=0;i<n;i++)ans|=(measure(i)<<i);
        return ans;
    }
};
const int maxn=(1<<20)+5;
int n,N,mx;
int w[maxn];
void Oracle(Qubits &st){
    for(int i=0;i<N;i++){
        if(w[i]!=mx)continue;
        st.a[i]*=-1;
    }
    return ;
}
void Diffusion(Qubits &st){
    for(int i=0;i<n;i++)st.apply_gate(H,i);
    for(int i=1;i<N;i++)st.a[i]*=-1;
    for(int i=0;i<n;i++)st.apply_gate(H,i);
    return ;
}
int main(){
    scanf("%d",&n);N=(1<<n);
    for(int i=0;i<N;i++)w[i]=i;
    shuffle(w,w+N,rnd);
    //for(int i=0;i<N;i++)cerr<<w[i]<<" ";cerr<<endl;
    for(int i=0;i<N;i++)mx=max(mx,w[i]);
    Qubits st(n);
    for(int i=0;i<n;i++)st.apply_gate(H,i);
    //for(int i=0;i<N;i++)cerr<<st.a[i].real()<<" "<<st.a[i].imag()<<endl;
    int T=pai/4*sqrt(N);//cerr<<T<<endl;
    while(T--)Oracle(st),Diffusion(st);
    //for(int i=0;i<N;i++)cerr<<norm(st.a[i])<<" ";
    //cerr<<endl;
    int pos=st.measure();
    printf("%d\n",pos);
    assert(w[pos]==mx);
    return 0;
}
