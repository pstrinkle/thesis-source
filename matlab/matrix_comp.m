% Matrix completion
%
% Given a matrix X1, we're going to say that it's ridiculously sparse, but
% there are no zero columns or rows.  And instead of feeding the program some
% random sampling, this feeds all non-zero entries and attempts to solve the
% zero entries.
%
% Think the Netflix problem.
%
% A matrix of movies x users where each cell value is their rating.  So the goal
%  is to fill the zero values in with non-zero values.  =)

load 1.tab;
% Let X1 be the matrix.

% Let “Omega” be the set of observed entries

% size(matrix_name) returns [row, col]
M = size(X1);

% Show the observed data
Y = nan(size(X1)); % This will fill Y with NaN's as a matrix NxN.

%
% NaN(M,N) or NaN([M,N]) is an M-by-N matrix of NaNs.
%
% M := row count
% N := col count
%

%
% This will take the number in X and set it in Y for each value in omega, which
% is a list j = [1, 2, 4, 5, 6]
% Y(j) = X(j) would set Y(1) = X(1), Y(2) = X(2), Y(4) = X(4), 
% leaving Y(3) == NaN
%
% What is non-obvious is that the indices go from 0th column, 0th row down to 
% 1st row, 0th column, so top to bottom, left to right.....
%
% fyi, indexing seems to start at 1 and not 0.
omega = find(X1);
Y(omega) = X(omega);
disp('The "NaN" entries represent unobserved values');
disp(Y)

% So what I would want here is to get a list of entries that are non-zero.
% ind = find(X) locates all nonzero elements of array X, and returns the linear 
% indices of those elements in vector ind.

% Run the completion code
observations = X(omega);    % the observed entries <-- amusingly my entries.
mu           = .001;        % smoothing parameter

% The solver runs in seconds
tic
Xk = solver_sNuclearBP( {M(1),M(2),omega}, observations, mu );
toc

% Show the recovered data

disp('Recovered matrix (rounding to nearest .0001):')
disp( round(Xk*10000)/10000 )
% and for reference, here is the original matrix:
disp('Original matrix:')
disp(X1)

% The relative error (without the rounding) is quite low:
%fprintf('Relative error, no rounding: %.8f%%\n', norm(X-Xk,'fro')/norm(X,'fro')*100 );
