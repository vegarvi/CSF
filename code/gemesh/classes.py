from domains_and_boundaries import *

bot_out = bottom_outer()
bot_in = bottom_inner()
out_wall = outer_wall()
in_wall = inner_wall()
top_out = top_outer()
top_in = top_inner()
csc_bnd = csc_boundary()
in_csc = inside_csc()
cord = cord()
CSF_s = CSF_space()

CSF_mesh = SubMesh(mesh,CSF_s)

boundaries = FacetFunction('size_t',mesh) # CSF_mesh
boundaries.set_all(0)


out_wall.mark(boundaries,1)
in_wall.mark(boundaries,1)
top_out.mark(boundaries,1)
bot_out.mark(boundaries,1)
bot_in.mark(boundaries,1)
top_in.mark(boundaries,1)
csc_bnd.mark(boundaries,1)

plot(boundaries)
interactive()
import sys
sys.exit()
noslip = Constant((0.0,0.0))

pb = Constant(0.0)
P = 1
pt = Expression(('P*(sin(2*pi*t) + 0.2*sin(8*pi*t))'),t=0,P=P)

flow = Expression(('0.0','(x[0]-x0)*(x[0]+x0)*(x[0]-x1)*(x[0]+x1)*pow(10,10)'),x0=x0,x1=x1)



V = VectorFunctionSpace(CSF_mesh,'CG',2)
Q = FunctionSpace(CSF_mesh,'CG',1)
u = TrialFunction(V)
v = TestFunction(V)
p = TrialFunction(Q)
q = TestFunction(Q)


inflow = DirichletBC(V,flow,boundaries, 3)
bcu0 = DirichletBC(V,noslip,boundaries, 1)
bcu1 = DirichletBC(V,noslip,boundaries, 2)

bcp1 = DirichletBC(Q,pt,boundaries, 3)
bcp2 = DirichletBC(Q, pb, boundaries ,4)


bcu = [bcu0,bcu1]#,bcu2,bcu3,bcu4]
bcp = [bcp1,bcp2]

eps = 1E-5
m_iter = 10


ufile = File('results/vel.pvd')
pfile = File('results/pr.pvd')

t = 0
T = 0.2
dt = 0.001

u0 = Function(V)#project(u0,V)
u1 = Function(V)
p1 = Function(Q)

# Define coefficients
k = Constant(dt)
f = Constant((0, 0))

# Tentative velocity step
F1 = (1/k)*inner(u - u0, v)*dx + inner(grad(u0)*u0, v)*dx + \
     nu*inner(grad(u), grad(v))*dx - inner(f, v)*dx
a1 = lhs(F1)
L1 = rhs(F1)

# Pressure update
a2 = inner(grad(p), grad(q))*dx
L2 = -(1/k)*div(u1)*q*dx

# Velocity update
a3 = inner(u, v)*dx + inner(u,v)*dx
L3 = inner(u1, v)*dx - k*inner(grad(p1), v)*dx

# Assemble matrices
A1 = assemble(a1)
A2 = assemble(a2)
A3 = assemble(a3)

# Use amg preconditioner if available
prec = "amg" if has_krylov_solver_preconditioner("amg") else "default"

n = FacetNormal(CSF_mesh)
n = FacetNormal(mesh)
n1 = as_vector((1.0,0))
n2 = as_vector((0,1.0))
nx = dot(n1,n)
ny = dot(n2,n)

while t < T + DOLFIN_EPS:
    pt.t = t

    # Update pressure boundary condition

    # Compute tentative velocity step
    begin("Computing tentative velocity")
    b1 = assemble(L1)
    [bc.apply(A1, b1) for bc in bcu]
    solve(A1, u1.vector(), b1, "gmres", "default")
    end()

    # Pressure correction
    begin("Computing pressure correction")
    b2 = assemble(L2)
    [bc.apply(A2, b2) for bc in bcp]
    solve(A2, p1.vector(), b2, "gmres", prec)
    end()

    # Velocity correction
    begin("Computing velocity correction")
    b3 = assemble(L3)
    [bc.apply(A3, b3) for bc in bcu]
    solve(A3, u1.vector(), b3, "gmres", "default")
    end()
	
    ufile << u1
    pfile << p1
    
    d = Expression(('-x[0]/std::abs(x[0])*0.0015*p/P*(-2*std::abs(x[0]) + 0.014)','0.0'),p=p1,t=t,P=P)
    
    #d = Expression(('-1000*p*abs(x[0]-0.007)*(x-0.007)*abs(x+0.007)*(x[0]+0.007)','0.0'),p=p1)
    
    

    disp = interpolate(d,V)
    CSF_mesh.move(disp)

    t += dt
    print "t =", t
    u0.assign(u1)
File('initial_data/u_double_refine.xml') << u0


