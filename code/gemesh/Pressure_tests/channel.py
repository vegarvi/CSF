from dolfin import *
from pylab import find, array
set_log_active(False)

ufile = File('results_channel/v.pvd')
pfile = File('results_channel/p.pvd')
h0 = 2
h1 = 10
L = 30

P1 = Point(0,0)
P2 = Point(L,h0)


mesh = Mesh('extend.xml')#RectangleMesh(P1,P2,10,50)

V = VectorFunctionSpace(mesh,'CG',2)
P = FunctionSpace(mesh,'CG',1)
VP = MixedFunctionSpace([V,P])

v,p = TrialFunctions(VP)
phi,eta = TestFunctions(VP)

eps = 1e-8

class Inlet(SubDomain):
	def inside(self,x,on_bnd):
		return x[0] < eps and on_bnd

class Outlet(SubDomain):
	def inside(self,x,on_bnd):
		return x[0] > L-eps and on_bnd

class Walls(SubDomain):
	def inside(self,x,on_bnd):
		b = x[0] > L-eps and abs(x[1]) < h1
		a = x[0] < eps and abs(x[1]) < h0
		return on_bnd and not (a or b)

bnd = FacetFunction('size_t',mesh)
Inlet().mark(bnd,2)
Outlet().mark(bnd,3)
Walls().mark(bnd,1)
noslip = Constant((0,0))
plot(bnd)
interactive()

bcs = [DirichletBC(VP.sub(0),noslip,bnd,1)]
ds = Measure('ds')[bnd]

rho_f = Constant(1./1000)		# g/mm
nu_f = Constant(0.658)			# mm**2/s
mu_f = Constant(nu_f*rho_f)		# g/(mm*s)

pressure = Expression('amp*sin(2*pi*t)',t=0,amp=0)
pressure2 = Expression('amp*sin(2*pi*t)',t=0,amp=0)
n = FacetNormal(mesh)


dt = 0.01
k = Constant(dt)
v0 = Function(V)
v1 = Function(V)



a = rho_f/k*inner(v,phi)*dx + \
	rho_f*inner(grad(v0)*v,phi)*dx - \
	inner(p,div(phi))*dx - \
	inner(eta,div(v))*dx + \
	2*mu_f*inner(sym(grad(v)),grad(phi))*dx - \
	mu_f*inner(grad(v).T*n,phi)*ds(2) - \
	mu_f*inner(grad(v).T*n,phi)*ds(3)


L = rho_f/k*inner(v1,phi)*dx  - \
	inner(pressure*n,phi)*ds(2) - \
	inner(pressure2*n,phi)*ds(3)

t = dt
T = dt
VP_ = Function(VP)


while t < T + DOLFIN_EPS:
	if t<2:
		pressure.amp = t
		pressure2.amp = -0.5*t
	pressure2.t=t
	pressure.t=t
	b = assemble(L)
	err = 10
	k_iter = 0
	max_iter = 5
	while err > 1E-6 and k_iter < max_iter:
		A = assemble(a)
		[bc.apply(A,b) for bc in bcs]
		solve(A,VP_.vector(),b,'lu')
		v_,p_ = VP_.split(True)
		err = errornorm(v_,v0,degree_rise=3)
		k_iter += 1
		print 'k: ',k_iter, 'error: %.3e' %err
		v0.assign(v_)
	#plot(v0)
	#interactive()
	ufile << v_
	pfile << p_
	v1.assign(v_)
	print 't=%.4f'%t
	t += dt


