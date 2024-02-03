import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.metrics import explained_variance_score


def get_rate_r2(analysis_source, analysis_targ):
    # Function to compare the rate-reconstruction of the different models
    rates_source = analysis_source.get_rates()
    n_b_source, n_t_source, n_d_source = rates_source.shape
    rates_source_flat = (
        rates_source.reshape(n_b_source * n_t_source, n_d_source).detach().numpy()
    )

    rates_targ = analysis_targ.get_rates()
    n_b_targ, n_t_targ, n_d_targ = rates_targ.shape
    rates_targ_flat = rates_targ.reshape(n_b_targ * n_t_targ, n_d_targ).detach().numpy()

    reg = LinearRegression().fit(rates_source_flat, rates_targ_flat)
    r2 = reg.score(rates_source_flat, rates_targ_flat)
    return r2


def get_state_r2(analysis_source, analysis_targ, num_pcs=3):
    # Function to compare the latent activity
    lats_source = analysis_source.get_latents()
    n_b_source, n_t_source, n_d_source = lats_source.shape
    lats_source_flat = (
        lats_source.reshape(n_b_source * n_t_source, n_d_source).detach().numpy()
    )
    pca = PCA(n_components=num_pcs)
    lats_source_flat_pca = pca.fit_transform(lats_source_flat)
    lats_source = lats_source_flat_pca.reshape((n_b_source, n_t_source, num_pcs))

    lats_targ = analysis_targ.get_latents()
    n_b_targ, n_t_targ, n_d_targ = lats_targ.shape
    lats_targ_flat = lats_targ.reshape(n_b_targ * n_t_targ, n_d_targ).detach().numpy()
    pca = PCA(n_components=num_pcs)
    lats_targ_flat_pca = pca.fit_transform(lats_targ_flat)
    lats_targ = lats_targ_flat_pca.reshape((n_b_targ, n_t_targ, num_pcs))

    # Compare the latent activity
    state_r2 = []
    for j in range(num_pcs):
        reg = LinearRegression().fit(lats_source_flat_pca, lats_targ_flat_pca[:, j])
        state_r2.append(reg.score(lats_source_flat_pca, lats_targ_flat_pca[:, j]))

    state_r2 = np.array(state_r2)
    return np.mean(state_r2)


def get_latents_vaf(analysis1, analysis2, num_pcs=3):
    lats1 = analysis1.get_latents()
    lats1_flat = (
        lats1.reshape(lats1.shape[0] * lats1.shape[1], lats1.shape[2]).detach().numpy()
    )
    pca = PCA(n_components=num_pcs)
    lats1_flat_pca = pca.fit_transform(lats1_flat)

    lats2 = analysis2.get_latents()
    lats2_flat = (
        lats2.reshape(lats2.shape[0] * lats2.shape[1], lats2.shape[2]).detach().numpy()
    )
    pca = PCA(n_components=num_pcs)
    lats2_flat_pca = pca.fit_transform(lats2_flat)
    reg = LinearRegression().fit(lats1_flat_pca, lats2_flat_pca)
    preds = reg.predict(lats1_flat_pca)
    var_exp = explained_variance_score(
        lats2_flat_pca, preds, multioutput="variance_weighted"
    )
    return var_exp
