a = 0.001*1000;
x0 = 0.005*1000;
x1 = 0.009*1000;
h = 0.06*1000;

Point(1) = {0, 0, 0, a};

Point(2) = {x0, 0, 0,a};
Point(3) = {x1, 0, 0,a};
Point(4) = {-x0,0,0,a};
Point(5) = {-x1,0,0,a};


Line(1) = {5, 4};
Line(2) = {4, 1};
Line(3) = {1, 2};
Line(4) = {2, 3};


Point(6) = {0, h, 0, a};

Point(7) = {x0, h, 0,a};
Point(8) = {x1, h, 0,a};
Point(9) = {-x0,h,0,a};
Point(10) = {-x1,h,0,a};

Line(5) = {2,7};
Line(6) = {3,8};
Line(7) = {4,9};
Line(8) = {5,10};

Line(9) = {10,9};
Line(10) = {9,6};
Line(11) = {6,7};
Line(12) = {7,8};

Line Loop(13) = {9, -7, -1, 8};
Plane Surface(14) = {13};
Line Loop(15) = {5, 12, -6, -4};
Plane Surface(16) = {15};
Line Loop(17) = {10, 11, -5, -3, -2, 7};
Plane Surface(18) = {17};
