# distutils: libraries = flint
# distutils: depends = flint/nmod_mat.h

from sage.libs.flint.types cimport *

cdef extern from "flint_wrap.h":
    mp_limb_t nmod_mat_get_entry(const nmod_mat_t mat, slong i, slong j);
    mp_limb_t * nmod_mat_entry_ptr(const nmod_mat_t mat, slong i, slong j);
    slong nmod_mat_nrows(const nmod_mat_t mat);
    slong nmod_mat_ncols(const nmod_mat_t mat);
    void _nmod_mat_set_mod(nmod_mat_t mat, mp_limb_t n);
    void nmod_mat_init(nmod_mat_t mat, slong rows, slong cols, mp_limb_t n);
    void nmod_mat_init_set(nmod_mat_t mat, const nmod_mat_t src);
    void nmod_mat_clear(nmod_mat_t mat);
    void nmod_mat_one(nmod_mat_t mat);
    void nmod_mat_swap(nmod_mat_t mat1, nmod_mat_t mat2);
    void nmod_mat_window_init(nmod_mat_t window, const nmod_mat_t mat, slong r1, slong c1, slong r2, slong c2);
    void nmod_mat_window_clear(nmod_mat_t window);
    void nmod_mat_randtest(nmod_mat_t mat, flint_rand_t state);
    void nmod_mat_randfull(nmod_mat_t mat, flint_rand_t state);
    void nmod_mat_randrank(nmod_mat_t, flint_rand_t state, slong rank);
    void nmod_mat_randops(nmod_mat_t mat, slong count, flint_rand_t state);
    void nmod_mat_randtril(nmod_mat_t mat, flint_rand_t state, int unit);
    void nmod_mat_randtriu(nmod_mat_t mat, flint_rand_t state, int unit);
    void nmod_mat_print_pretty(const nmod_mat_t mat);
    int nmod_mat_equal(const nmod_mat_t mat1, const nmod_mat_t mat2);
    void nmod_mat_zero(nmod_mat_t mat);
    int nmod_mat_is_zero(const nmod_mat_t mat);
    int nmod_mat_is_zero_row(const nmod_mat_t mat, slong i)
    int nmod_mat_is_empty(const nmod_mat_t mat);
    int nmod_mat_is_square(const nmod_mat_t mat);
    void nmod_mat_set(nmod_mat_t B, const nmod_mat_t A);
    void nmod_mat_transpose(nmod_mat_t B, const nmod_mat_t A);
    void nmod_mat_add(nmod_mat_t C, const nmod_mat_t A, const nmod_mat_t B);
    void nmod_mat_sub(nmod_mat_t C, const nmod_mat_t A, const nmod_mat_t B);
    void nmod_mat_neg(nmod_mat_t B, const nmod_mat_t A);
    void nmod_mat_scalar_mul(nmod_mat_t B, const nmod_mat_t A, mp_limb_t c);
    void nmod_mat_scalar_mul_fmpz(nmod_mat_t res, const nmod_mat_t M, const fmpz_t c);
    void nmod_mat_mul(nmod_mat_t C, const nmod_mat_t A, const nmod_mat_t B);
    int nmod_mat_mul_blas(nmod_mat_t C, const nmod_mat_t A, const nmod_mat_t B);
    void nmod_mat_mul_classical(nmod_mat_t C, const nmod_mat_t A, const nmod_mat_t B);
    void nmod_mat_mul_strassen(nmod_mat_t C, const nmod_mat_t A, const nmod_mat_t B);
    void _nmod_mat_pow(nmod_mat_t dest, const nmod_mat_t mat, ulong pow);
    void nmod_mat_pow(nmod_mat_t dest, const nmod_mat_t mat, ulong pow);
    mp_limb_t nmod_mat_trace(const nmod_mat_t mat);
    mp_limb_t _nmod_mat_det(nmod_mat_t A);
    mp_limb_t nmod_mat_det(const nmod_mat_t A);
    slong nmod_mat_rank(const nmod_mat_t A);
    int nmod_mat_inv(nmod_mat_t B, const nmod_mat_t A);
    void nmod_mat_swap_rows(nmod_mat_t mat, slong * perm, slong r, slong s);
    void nmod_mat_invert_rows(nmod_mat_t mat, slong * perm);
    void nmod_mat_swap_cols(nmod_mat_t mat, slong * perm, slong r, slong s);
    void nmod_mat_invert_cols(nmod_mat_t mat, slong * perm);
    void nmod_mat_apply_permutation(nmod_mat_t A, slong * P, slong n);
    void nmod_mat_solve_tril(nmod_mat_t X, const nmod_mat_t L, const nmod_mat_t B, int unit);
    void nmod_mat_solve_tril_recursive(nmod_mat_t X, const nmod_mat_t L, const nmod_mat_t B, int unit);
    void nmod_mat_solve_tril_classical(nmod_mat_t X, const nmod_mat_t L, const nmod_mat_t B, int unit);
    void nmod_mat_solve_triu(nmod_mat_t X, const nmod_mat_t U, const nmod_mat_t B, int unit);
    void nmod_mat_solve_triu_recursive(nmod_mat_t X, const nmod_mat_t U, const nmod_mat_t B, int unit);
    void nmod_mat_solve_triu_classical(nmod_mat_t X, const nmod_mat_t U, const nmod_mat_t B, int unit);
    slong nmod_mat_lu(slong * P, nmod_mat_t A, int rank_check);
    slong nmod_mat_lu_classical(slong * P, nmod_mat_t A, int rank_check);
    slong nmod_mat_lu_recursive(slong * P, nmod_mat_t A, int rank_check);
    int nmod_mat_solve(nmod_mat_t X, const nmod_mat_t A, const nmod_mat_t B);
    int nmod_mat_solve_vec(mp_ptr x, const nmod_mat_t A, mp_srcptr b);
    slong nmod_mat_rref(nmod_mat_t A);
    slong _nmod_mat_rref(nmod_mat_t A, slong * pivots_nonpivots, slong * P);
    slong nmod_mat_rref_classical(nmod_mat_t A);
    slong _nmod_mat_rref_classical(nmod_mat_t A, slong * pivots_nonpivots);
    slong nmod_mat_rref_storjohann(nmod_mat_t A);
    slong _nmod_mat_rref_storjohann(nmod_mat_t A, slong * pivots_nonpivots);
    slong nmod_mat_reduce_row(nmod_mat_t M, slong * P, slong * L, slong m);
    slong nmod_mat_nullspace(nmod_mat_t X, const nmod_mat_t A);
    void nmod_mat_strong_echelon_form(nmod_mat_t A);
    slong nmod_mat_howell_form(nmod_mat_t A);
    void nmod_mat_similarity(nmod_mat_t M, slong r, ulong d);
    void nmod_mat_set_entry(nmod_mat_t mat, slong i, slong j, mp_limb_t x);
