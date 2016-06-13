// PCA
// Code Modified By
// Patrick Trinkle
//

/* 
 * Principal Components Analysis or the Karhunen-Loeve expansion is a
 * classical method for dimensionality reduction or exploratory data
 * analysis.  One reference among many is: F. Murtagh and A. Heck,
 * Multivariate Data Analysis, Kluwer Academic, Dordrecht, 1987.
 * 
 * Author:
 * F. Murtagh
 * Phone:        + 49 89 32006298 (work)
 * + 49 89 965307 (home)
 * Earn/Bitnet:  fionn@dgaeso51,  fim@dgaipp1s,  murtagh@stsci
 * Span:         esomc1::fionn
 * Internet:     murtagh@scivax.stsci.edu
 *
 * F. Murtagh, Munich, 6 June 1989                                  
 */

#include <dirent.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>

/* buffer length stuff */
#define MAX_PATH_LENGTH 1024

//#define PRINT_STATUS

/**
 * @brief This guy walks through the file and sets the counts.
 */
static int
process_file(const char *filepath);

/**
 * @brief This will hold the counts for the file that's being read in.
 */
static uint32_t *user_terms_counts;

#define SIGN(a, b) ( (b) < 0 ? -fabs(a) : fabs(a) )

static float *vector(int n);
static float **matrix(int n, int m);

static void free_matrix(float **mat, int n);
static void free_vector(float *v);

static void tred2(float **a, int n, float *d, float *e);
static void tqli(float d[], float e[], int n, float **z);

static void corcol(float **data, int n, int m, float **symmat);
static void scpcol(float **data, int n, int m, float **symmat);
static void covcol(float **data, int n, int m, float **symmat);

/**
 * @brief Print usage information.
 */
static void
usage(void)
{
    fprintf(stderr, "./program NUM_DOCUMENTS NUM_TERMS INPUT_FOLDER\n");

    return;
}

/**
 * @brief Main execution path.
 */
int main(int argc, char *argv[])
{
	FILE *stream;

	int  done, n, m, i, j, k, k2;
    float **data, **symmat, **symmat2, *evals, *interm;
    float in_value;
    struct dirent *xp = NULL;
    
    /*
     * All of this code was written by someone considerably more familiar with
     * fortran/matlab because it's all 1 based indexing..!
     */
    if (argc < 4)
    {
        usage( );
        exit(-1);
    }
    
    n = atoi(argv[1]); // n is the number of users (documents).
    m = atoi(argv[2]); // m is the number of terms.

    user_terms_counts = malloc(m * sizeof(uint32_t));

    char option='V';
    char names[n+1][MAX_PATH_LENGTH];

	data = matrix(n, m);  // Storage allocation for input data

	// start processing files in user directory
	DIR *user = opendir(argv[3]);
    int pathlen = strlen(argv[3]);

	if (NULL == user)
    {
		printf("%s failed to open.\n", argv[3]);
		return 0;
	}

    /* used to index data[doc]. */
    i = 1;

	while ((xp = readdir(user)) != NULL)
    {
        int filenamelen = 0;
        char ftmp[MAX_PATH_LENGTH];

        bzero(ftmp, sizeof(ftmp));

		if (strncmp(xp->d_name, ".", 1) != 0)
        {
            filenamelen = strlen(xp->d_name);
            //printf("file: %s\n", xp->d_name);
            
            strncpy(ftmp, argv[3], pathlen);
            strncat(ftmp, "/", 1);
            strncat(ftmp, xp->d_name, filenamelen);

            if (process_file(ftmp))
            {
                fprintf(stderr, "failed to process file, aborting!\n");

                free(user_terms_counts);
                closedir(user);

                goto exit;
            }

            strncpy(names[i], xp->d_name, filenamelen);

            for (j = 0; j < m; j++)
            {
                data[i][j+1] = user_terms_counts[j];
            }
            
            i++;
		}
	}
    
    free(user_terms_counts);
	closedir(user);

	printf("Finished processing input.\n");

	symmat = matrix(m, m);  /* Allocation of correlation (etc.) matrix */

	/* Look at analysis option; branch in accordance with this. */

	switch(option)
	{
        case 'R':
        case 'r':
            printf("Analysis of correlations chosen.\n");
            corcol(data, n, m, symmat);
            break;
        case 'V':
        case 'v':
            printf("Analysis of variances-covariances chosen.\n");
            covcol(data, n, m, symmat);
            break;
        case 'S':
        case 's':
            printf("Analysis of sums-of-squares-cross-products");
            printf(" matrix chosen.\n");
            scpcol(data, n, m, symmat);
            break;
        default:
            printf("Option: %c\n", option);
            printf("For option, please type R, V, or S\n");
            printf("(upper or lower case).\n");
            printf("Exiting to system.\n");
            exit(1);
            break;
	}

	/*********************************************************************
	 * Eigen-reduction
	 **********************************************************************/

	/* Allocate storage for dummy and new vectors. */
	evals = vector(m);      /* Storage alloc. for vector of eigenvalues */
	interm = vector(m);     /* Storage alloc. for 'intermediate' vector */
	symmat2 = matrix(m, m); /* Duplicate of correlation (etc.) matrix */

	/* They could have just looped the i's and memcpy'd the data. */
	for (i = 1; i <= m; i++)
    {
		for (j = 1; j <= m; j++)
        {
			symmat2[i][j] = symmat[i][j]; /* Needed below for col. projections */
		}
	}
    
	tred2(symmat, m, evals, interm);  /* Triangular decomposition */
	tqli(evals, interm, m, symmat);   /* Reduction of sym. trid. matrix */
    
	/* 
     * evals now contains the eigenvalues,
	 * columns of symmat now contain the associated eigenvectors.
     */

	printf("eigenvalues computed.\n");
    
#ifdef PRINT_STATUS
	printf("\nEigenvalues:\n");
	for (j = m; j >= 1; j--)
    {
		printf("%18.5f\n", evals[j]);
    }

	printf("\n(Eigenvalues should be strictly positive; limited\n");
	printf("precision machine arithmetic may affect this.\n");
	printf("Eigenvalues are often expressed as cumulative\n");
	printf("percentages, representing the 'percentage variance\n");
	printf("explained' by the associated axis or principal component.)\n");

	printf("\nEigenvectors:\n");
	printf("(First three; their definition in terms of original vbes.)\n");

	for (j = 1; j <= m; j++)
    {
		for (i = 1; i <= 3; i++)
        {
			printf("%12.4f", symmat[j][m-i+1]);
        }
		printf("\n");
    }
#endif

	/* Form projections of row-points on first three prin. components. */
	/* Store in 'data', overwriting original data. */
	for (i = 1; i <= n; i++)
    {
	    /* memcpy would have worked as well. */
		for (j = 1; j <= m; j++)
        {
			interm[j] = data[i][j];
        }   /* data[i][j] will be overwritten */

		for (k = 1; k <= 3; k++)
        {
			data[i][k] = 0.0;
            
			for (k2 = 1; k2 <= m; k2++)
            {
				data[i][k] += interm[k2] * symmat[k2][m-k+1];
            }
		}
	}

	if ((stream = fopen("rowpts.dat", "w")) == NULL)
	{
		fprintf(stderr, "Program %s : cannot open file %s\n", argv[0], "rowpts.dat");
		fprintf(stderr, "Exiting to system.");
		exit(1);
	}
    
//#ifdef PRINT_STATUS
	printf("\nCreating rowpts.dat file - Projections of row-points on first 3 prin. comps.:\n");
//#endif
    
	for (i = 1; i <= n; i++)
    {
		for (j = 1; j <= 4; j++)
        {
			if (j == 4)
            {
				fprintf(stream, "\t%s", names[i]);  
			}
			else
            {
				fprintf(stream, "%12.4f", data[i][j]);  
			}
		}
        
		fprintf(stream,"\n");  
	}

	fclose(stream);

	/* Form projections of col.-points on first three prin. components. */
	/* Store in 'symmat2', overwriting what was stored in this. */
	for (j = 1; j <= m; j++)
    {
	    /* memcpy */
		for (k = 1; k <= m; k++)
        {
			interm[k] = symmat2[j][k];
        }  /*symmat2[j][k] will be overwritten*/
        
		for (i = 1; i <= 3; i++)
        {
			symmat2[j][i] = 0.0;
            
			for (k2 = 1; k2 <= m; k2++)
            {
				symmat2[j][i] += interm[k2] * symmat[k2][m-i+1];
            }
            
			if (evals[m-i+1] > 0.0005)   /* Guard against zero eigenvalue */
            {
				symmat2[j][i] /= sqrt(evals[m-i+1]);   /* Rescale */
            }
			else
            {
				symmat2[j][i] = 0.0;    /* Standard kludge */
            }
		}
	}

	if ((stream = fopen("colpts.dat", "w")) == NULL)
	{
		fprintf(stderr, "Program %s : cannot open file %s\n", argv[0], "colpts.dat");
		fprintf(stderr, "Exiting to system.");
		exit(1);
	}
    
#ifdef PRINT_STATUS
	printf("\nCreating colpts.dat file - Projections of column-points on first 3 prin. comps.:\n");
#endif	
    
	for (j = 1; j <= m; j++)
    {
		for (k = 1; k <= 3; k++)
        {
			fprintf(stream,"%12.4f", symmat2[j][k]);
        }
        
		fprintf(stream,"\n");
    }
    
	fclose(stream);

exit:
    if (data)
        free_matrix(data, n);
    if (symmat)
        free_matrix(symmat, m);
    if (symmat2)
        free_matrix(symmat2, m);
    if (evals)
        free_vector(evals);
    if (interm)
        free_vector(interm);

    return 0;
}

/**  Correlation matrix: creation  ***********************************/

/* Create m * m correlation matrix from given n * m data matrix. */
static void
corcol(float **data, int n, int m, float **symmat)
{
	float eps = 0.005;
	float x, *mean, *stddev, *vector();
	int i, j, j1, j2;

	/* Allocate storage for mean and std. dev. vectors */

	mean = vector(m);
	stddev = vector(m);

	/* Determine mean of column vectors of input data matrix */

	for (j = 1; j <= m; j++)
	{
		mean[j] = 0.0;
		for (i = 1; i <= n; i++)
		{
			mean[j] += data[i][j];
		}
		mean[j] /= (float)n;
	}
    
#ifdef PRINT_STATUS
	printf("\nMeans of column vectors:\n");
	for (j = 1; j <= m; j++)
    {
		printf("%7.1f", mean[j]);
    }
    printf("\n");
#endif
    
    /* Determine standard deviations of column vectors of data matrix. */

    for (j = 1; j <= m; j++)
    {
        stddev[j] = 0.0;
        for (i = 1; i <= n; i++)
        {
            stddev[j] += ((data[i][j] - mean[j]) * (data[i][j] - mean[j]));
        }
        
        stddev[j] /= (float)n;
        stddev[j] = sqrt(stddev[j]);
        /*
         * The following in an inelegant but usual way to handle near-zero
         * std. dev. values, which below would cause a zero-divide.
         */
        if (stddev[j] <= eps)
        {
            stddev[j] = 1.0;
        }
    }

    printf("\nStandard deviations of columns:\n");
    for (j = 1; j <= m; j++)
    {
        printf("%7.1f", stddev[j]);
    }
    printf("\n");

    /* Center and reduce the column vectors. */
    
    for (i = 1; i <= n; i++)
    {
        for (j = 1; j <= m; j++)
        {
            data[i][j] -= mean[j];
            x = sqrt((float)n);
            x *= stddev[j];
            data[i][j] /= x;
        }
    }

    /* Calculate the m * m correlation matrix. */
    for (j1 = 1; j1 <= m-1; j1++)
    {
        symmat[j1][j1] = 1.0;
        for (j2 = j1+1; j2 <= m; j2++)
        {
            symmat[j1][j2] = 0.0;
            for (i = 1; i <= n; i++)
            {
                symmat[j1][j2] += (data[i][j1] * data[i][j2]);
            }
            symmat[j2][j1] = symmat[j1][j2];
        }
    }
    symmat[m][m] = 1.0;

    return;
}

/**  Variance-covariance matrix: creation  *****************************/

/* Create m * m covariance matrix from given n * m data matrix. */
static void
covcol(float **data, int n, int m, float **symmat)
{
	float *mean, *vector();
	int i, j, j1, j2;

	/* Allocate storage for mean vector */
	mean = vector(m);

	/* Determine mean of column vectors of input data matrix */
	for (j = 1; j <= m; j++)
	{
		mean[j] = 0.0;
		for (i = 1; i <= n; i++)
		{
			mean[j] += data[i][j];
		}
		mean[j] /= (float)n;
	}
    
#ifdef PRINT_STATUS
	printf("\nMeans of column vectors:\n");
	for (j = 1; j <= m; j++)
    {
		printf("%7.1f",mean[j]);
    }
    printf("\n");
#endif
    
    /* Center the column vectors. */
    for (i = 1; i <= n; i++)
    {
        for (j = 1; j <= m; j++)
        {
            data[i][j] -= mean[j];
        }
    }

    /* Calculate the m * m covariance matrix. */
    for (j1 = 1; j1 <= m; j1++)
    {
        for (j2 = j1; j2 <= m; j2++)
        {
            symmat[j1][j2] = 0.0;
            for (i = 1; i <= n; i++)
            {
                symmat[j1][j2] += data[i][j1] * data[i][j2];
            }
            symmat[j2][j1] = symmat[j1][j2];
        }
    }
    
    return;
}

/**  Sums-of-squares-and-cross-products matrix: creation  **************/

/* Create m * m sums-of-cross-products matrix from n * m data matrix. */
static void
scpcol(float **data, int n, int m, float **symmat)
{
	int i, j1, j2;

	/* Calculate the m * m sums-of-squares-and-cross-products matrix. */
	for (j1 = 1; j1 <= m; j1++)
	{
		for (j2 = j1; j2 <= m; j2++)
		{
			symmat[j1][j2] = 0.0;

			for (i = 1; i <= n; i++)
			{
				symmat[j1][j2] += data[i][j1] * data[i][j2];
			}

			symmat[j2][j1] = symmat[j1][j2];
		}
	}

	return;
}

/**  Error handler  **************************************************/

/* Error handler */
static void erhand(char err_msg[])
{
	fprintf(stderr, "Run-time error:\n%s\n", err_msg);
	fprintf(stderr, "Exiting to system.\n");

	exit(1);
}

/**  Allocation of vector storage  ***********************************/

/* Allocates a float vector with range [1..n]. */
static float *vector(int n)
{
	float *v;

	v = (float *) malloc ((unsigned) n*sizeof(float));

	if (!v)
	{
	    erhand("Allocation failure in vector().");
	}

	/*
	 * They do this because they don't allocate n+1 items, they just return a
	 * pointer to the memory before the array and never index 0.  Really dumb.
	 */
	return v-1;
}

/**  Allocation of float matrix storage  *****************************/

/* Allocate a float matrix with range [1..n][1..m]. */
static float **matrix(int n, int m)
{
	int i;
	float **mat;

	/* Allocate pointers to rows. */
	mat = (float **) malloc((unsigned) (n)*sizeof(float*));
    
	if (!mat)
    {
        erhand("Allocation failure 1 in matrix().");   
    }
    
	mat -= 1;

	/* Allocate rows and set pointers to them. */
	for (i = 1; i <= n; i++)
	{
		mat[i] = (float *) malloc((unsigned) (m)*sizeof(float));

		if (!mat[i])
        {
            erhand("Allocation failure 2 in matrix().");
        }
		mat[i] -= 1;
	}

	/* Return pointer to array of pointers to rows. */
	return mat;
}

/**  Deallocate vector storage  *********************************/

/* Free a float vector allocated by vector(). */
static void
free_vector(float *v)
{
	free((char*) (v+1));

	return;
}

/**  Deallocate float matrix storage  ***************************/

/* Free a float matrix allocated by matrix(). */
static void
free_matrix(float **mat, int n)
{
	int i;

	for (i = n; i >= 1; i--)
	{
		free ((char*) (mat[i]+1));
	}

	free ((char*) (mat+1));

	return;
}

/**  Reduce a real, symmetric matrix to a symmetric, tridiag. matrix. */

/*
 * Householder reduction of matrix a to tridiagonal form.
 * Algorithm: Martin et al., Num. Math. 11, 181-195, 1968.
 * Ref: Smith et al., Matrix Eigensystem Routines -- EISPACK Guide
 * Springer-Verlag, 1976, pp. 489-494.
 * W H Press et al., Numerical Recipes in C, Cambridge U P,
 * 1988, pp. 373-374.
 */
/* float **a, d[], e[]; */
static void
tred2(float **a, int n, float *d, float *e)
{
	int l, k, j, i;
	float scale, hh, h, g, f;

	for (i = n; i >= 2; i--)
	{
		l = i - 1;
		h = scale = 0.0;

		if (l > 1)
		{
			for (k = 1; k <= l; k++)
            {
				scale += fabs(a[i][k]);
            }
            
			if (scale == 0.0)
            {
				e[i] = a[i][l];
            }
			else
			{
				for (k = 1; k <= l; k++)
				{
					a[i][k] /= scale;
					h += a[i][k] * a[i][k];
				}
                
				f = a[i][l];
				g = f > 0 ? -sqrt(h) : sqrt(h);
				e[i] = scale * g;
				h -= f * g;
				a[i][l] = f - g;
				f = 0.0;
                
				for (j = 1; j <= l; j++)
				{
					a[j][i] = a[i][j]/h;
					g = 0.0;
                    
					for (k = 1; k <= j; k++)
					{
						g += a[j][k] * a[i][k];
					}
                    
					for (k = j+1; k <= l; k++)
					{
						g += a[k][j] * a[i][k];
					}
                    
					e[j] = g / h;
					f += e[j] * a[i][j];
				}
                
				hh = f / (h + h);
                
				for (j = 1; j <= l; j++)
				{
					f = a[i][j];
					e[j] = g = e[j] - hh * f;
                    
					for (k = 1; k <= j; k++)
					{
						a[j][k] -= (f * e[k] + g * a[i][k]);
					}
				}
			}
		}
		else
        {
			e[i] = a[i][l];
        }
		d[i] = h;
	}
    
	d[1] = 0.0;
	e[1] = 0.0;
    
	for (i = 1; i <= n; i++)
	{
		l = i - 1;

		if (d[i])
		{
			for (j = 1; j <= l; j++)
			{
				g = 0.0;
                
				for (k = 1; k <= l; k++)
				{
					g += a[i][k] * a[k][j];
				}
                
				for (k = 1; k <= l; k++)
				{
					a[k][j] -= g * a[k][i];
				}
			}
		}
        
		d[i] = a[i][i];
		a[i][i] = 1.0;
        
		for (j = 1; j <= l; j++)
		{
			a[j][i] = a[i][j] = 0.0;
		}
	}

	return;
}

/**  Tridiagonal QL algorithm -- Implicit  **********************/
static void
tqli(float d[], float e[], int n, float **z)
{
	int m, l, iter, i, k;
	float s, r, p, g, f, dd, c, b;
	void erhand();

	for (i = 2; i <= n; i++)
    {
		e[i-1] = e[i];
    }
    
	e[n] = 0.0;
    
	for (l = 1; l <= n; l++)
	{
		iter = 0;

		do
		{
			for (m = l; m <= n-1; m++)
			{
				dd = fabs(d[m]) + fabs(d[m+1]);

				if (fabs(e[m]) + dd == dd)
                {
                    break;
                }
			}

			if (m != l)
			{
				if (iter++ == 30)
                {
                    erhand("No convergence in TLQI.");
                }

				g = (d[l+1] - d[l]) / (2.0 * e[l]);
				r = sqrt((g * g) + 1.0);
				g = d[m] - d[l] + e[l] / (g + SIGN(r, g));
				s = c = 1.0;
				p = 0.0;
                
				for (i = m-1; i >= l; i--)
				{
					f = s * e[i];
					b = c * e[i];
                    
					if (fabs(f) >= fabs(g))
					{
						c = g / f;
						r = sqrt((c * c) + 1.0);
						e[i+1] = f * r;
						c *= (s = 1.0/r);
					}
					else
					{
						s = f / g;
						r = sqrt((s * s) + 1.0);
						e[i+1] = g * r;
						s *= (c = 1.0/r);
					}
                    
					g = d[i+1] - p;
					r = (d[i] - g) * s + 2.0 * c * b;
					p = s * r;
					d[i+1] = g + p;
					g = c * r - b;
                    
					for (k = 1; k <= n; k++)
					{
						f = z[k][i+1];
						z[k][i+1] = s * z[k][i] + c * f;
						z[k][i] = c * z[k][i] - s * f;
					}
				}
                
				d[l] = d[l] - p;
				e[l] = g;
				e[m] = 0.0;
			}
		} while (m != l);
	}

	return;
}

static int
process_file(
    const char *filepath)
{
    /* Open file, read in each number. */
	FILE *fd = fopen(filepath, "r");
	if (fd == NULL)
    {
		printf("could not open: %s\n", filepath);
		return -1;
	}

    int i = 0;

    char *line = NULL;
    size_t linecap = 0;
    ssize_t linelen;

    while ((linelen = getline(&line, &linecap, fd)) > 0)
    {
        user_terms_counts[i] = atoi(line);
        
        i++;
    }
    
    fclose(fd);
    
    free(line);
    
    return 0;
}



