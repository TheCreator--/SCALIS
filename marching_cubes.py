# Mapping from vertex_index to 4 bit number, where each bit corresponds to an edge.
edge_table = (
	0b0000,
	0b1001,
	0b0011,
	0b1010,
	0b0110,
	0b1111,
	0b0101,
	0b1100,
	0b1100,
	0b0101,
	0b1111,
	0b0110,
	0b1010,
	0b0011,
	0b1001,
	0b0000
)

# Mapping from vertex_index to tuple that corresponds to which edges form an edge.
triangle_table = (
	(),
	((0, 3),),
	((0, 1),),
	((1, 3),),
	((1, 2),),
	((0, 1),( 2, 3),),
	((0, 2),),
	((2, 3),),
	((2, 3),),
	((0, 2),),
	((0, 3), (1, 2),),
	((1, 2),),
	((1, 3),),
	((0, 1),),
	((0, 3),),
	()
)


def lerp(P1, P2, V1, V2, isolevel):
	P = [0, 0]
	P[0] = P1[0] + (isolevel - V1)*(P2[0] - P1[0])/(V2 - V1)
	P[1] = P1[1] + (isolevel - V1)*(P2[1] - P1[1])/(V2 - V1)
	return P

def polygonize(cell, values, isolevel):

	# Figure out which vertices of the square are inside of the surface
	vertex_index = 0
	if values[0] < isolevel: vertex_index |= 0b0001;
	if values[1] < isolevel: vertex_index |= 0b0010;
	if values[2] < isolevel: vertex_index |= 0b0100;
	if values[3] < isolevel: vertex_index |= 0b1000;

	# If the square doesn't intersect the surface, we are done.
	if edge_table[vertex_index] == 0:
		return []
	
	# For every edge we intersect, get the point of intersection.
	edge_list = [[], [], [], []]
	if edge_table[vertex_index] & 0b0001:
		edge_list[0] = lerp(cell[0], cell[1], values[0], values[1], isolevel)
	if edge_table[vertex_index] & 0b0010:
		edge_list[1] = lerp(cell[1], cell[2], values[1], values[2], isolevel)
	if edge_table[vertex_index] & 0b0100:
		edge_list[2] = lerp(cell[2], cell[3], values[2], values[3], isolevel)
	if edge_table[vertex_index] & 0b1000:
		edge_list[3] = lerp(cell[3], cell[0], values[3], values[0], isolevel)

	# Get the edges forming the isosurface.
	return [(edge_list[e1], edge_list[e2]) for e1, e2 in triangle_table[vertex_index]]
