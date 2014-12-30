import re
import json
from math import log, sqrt

from jinja2 import Markup
from sklearn import cluster
from sklearn.decomposition import PCA
from scipy import stats
from sklearn import metrics
import numpy

from db import export_sql
from werkzeug.wrappers import Response

# create higher order transformations
def x2fs(X, fields, type=''):
    if type == 'Interaction':
        s2 = lambda x: x + 1
        e2 = lambda x, y: y
    elif type == 'Quadratic':
        s2 = lambda x: x
        e2 = lambda x, y: y
    elif type == 'Purely Quadratic':
        s2 = lambda x: x
        e2 = lambda x, y: x + 1
    else:
        return

    l1 = len(X[0])
    l2 = len(X[0])

    for i in range(len(X)):
        r = X[i]
        for j1 in range(l1):
            for j2 in range(s2(j1), e2(j1, l2)):
                r.append(r[j1] * r[j2])

    for j1 in range(l1):
        for j2 in range(s2(j1), e2(j1, l2)):
            fields.append(fields[j1] + '*' + fields[j2])


# fit_transform from sklearn doesn't return the loadings V. Here is a hacked version
def fit_transform(pca, X):
    U, S, V = pca._fit(X)

    if pca.whiten:
        # X_new = X * V / S * sqrt(n_samples) = U * sqrt(n_samples)
        U *= sqrt(X.shape[0])
    else:
        # X_new = X * V = U * S * V^T * V = U * S
        U *= S
    # transposing component matrix such that PCA_1 is in row
    V = V.transpose()
    return (U, V)


def evaluate(clust_dists, clustidx, X):
    results = {}
    sum = 0
    count = 0
    clustsum = [0 for i in range(len(clust_dists[0]))]
    clustcount = [0 for i in range(len(clust_dists[0]))]
    clustmean = [0 for i in range(len(clust_dists[0]))]
    for i in range(len(clustidx)):
        sum += clust_dists[i][clustidx[i]]
        count += 1

        clustsum[clustidx[i]] += clust_dists[i][clustidx[i]]
        clustcount[clustidx[i]] += 1

    averagedist = float(sum) / count

    results['meandist'] = averagedist

    for i in range(len(clust_dists[0])):
        clustmean[i] = float(clustsum[i]) / clustcount[i]

    return results, clustmean


def render(vis, request, info):
    info["message"] = []
    info["results"] = []

    # module independent user inputs
    table = request.args.get("table", '')
    where = request.args.get("where", '1=1')
    limit = request.args.get("limit", '1000')
    start = request.args.get("start", '0')  # start at 0
    reload = int(request.args.get("reload", 0))
    view = request.args.get("view", '')

    # module dependent user inputs
    field = request.args.get("field", '')
    pre_process = request.args.get("pre_process", '')
    pre_transform = request.args.get("pre_transform", '')

    orderBy = request.args.get("orderBy", '')
    groupBy = request.args.get("groupBy", '')
    if orderBy and len(orderBy) > 0: orderBy = ' order by %s' % orderBy
    if groupBy and len(groupBy) > 0: groupBy = ' group by %s' % groupBy

    k = int(request.args.get("k", 2))
    pfield = request.args.get("pfield", [])

    # verify essential parameter details - smell test
    if len(table) == 0 or len(field) == 0:
        info["message"].append("Table or field missing")
        info["message_class"] = "failure"
    else:
        # prepare sql query
        sql = "select %s from %s where %s %s %s limit %s offset %s" % (
        field, table, where, groupBy, orderBy, limit, start)

        (datfile, reload, result) = export_sql(sql, vis.config, reload, None, view)

        if len(result) > 0:
            info["message"].append(result)
            info["message_class"] = "failure"
        else:
            X = []
            with open(datfile, 'r') as f:
                for r in f:
                    row = r.rstrip().split(',')
                    X.append([float(r) for r in row])

            xfield = pfield
            # transform features
            x2fs(X, xfield, pre_transform)
            pfield = xfield

            X = numpy.array(X)

            if pre_process == "Z-Score":
                X = stats.zscore(X, axis=0)
            elif pre_process == "PCA":
                pca = PCA()
                (X, V) = fit_transform(pca, X)
                pfield = ['PCA_%d' % (d + 1) for d in range(len(pfield))]
            elif pre_process == "Whitened PCA":
                pca = PCA(whiten=True)
                (X, V) = fit_transform(pca, X)
                pfield = ['PCA_%d' % (d + 1) for d in range(len(pfield))]

            clust = cluster.KMeans(n_clusters=k)
            cidx = clust.fit_predict(X)
            cdists = clust.transform(X)


            # summary results
            results, clustmeans = evaluate(cdists, cidx, X)
            info["results"].append('Clustering the data using K-means with k=%d' % k)
            info["results"].append('Average distance to centroid: %.4f' % results['meandist'])

            hashquery = datfile + hex(hash(request.args.get('query', datfile)) & 0xffffffff)

            if pre_process == "PCA" or pre_process == "Whitened PCA":
                #write pca matrix file
                info["datfile_matrix"] = hashquery + '.pca.csv'
                with open(info["datfile_matrix"], 'w') as f:
                    f.write("feature,%s\n" % (','.join(xfield)))
                    for i in range(len(V)):
                        f.write('PCA_%d,%s\n' % (i + 1, ','.join([str(v) for v in V[i]])))
                info["pca_matrix_divs"] = Markup('<h2>PCA Components</h2><div id="svg-pca_matrix"></div>')
            else:
                info["pca_matrix_divs"] = ''

            # preparing within cluster distances into a js array
            f = []
            for i in range(k):
                f.append('{cluster:"%d", distance:%.3f}' % (i, clustmeans[i]))
            info["clust_data"] = Markup('clust_data=[' + ','.join(f) + '];')

            #provenance
            #0:id,1:prediction result (grouping),2:actual label(shape),3:error,4:y,or features
            info["datfile_provenance"] = hashquery + '.provenance.csv'
            RES = ['Cluster %d' % (i + 1) for i in range(k)]
            with open(info["datfile_provenance"], 'w') as f:
                f.write('Cluster,Error,%s\n' % (','.join(pfield)))
                for i in range(len(cidx)):
                    e = cdists[i][cidx[i]]
                    f.write('%s,%.4f,%s\n' % (RES[cidx[i]], e, ','.join([str(r) for r in X[i]])))

            pfield = ['cluster'] + pfield
            divs = [
                '<div class="chart"><div class="title">%s<a href="javascript:reset(%d)" class="reset" style="display: none;">reset</a></div></div>' % (
                pfield[d], d + 1) for d in range(len(pfield))]
            divs = ''.join(divs)
            divs = '<div class="chart"><div class="title">Distance to Centroid (<span id="active"></span> of <span id="total"></span> items selected.)<a href="javascript:reset(0)" class="reset" style="display: none;">reset</a></div></div>' + divs
            info['provenance_divs'] = Markup(divs)

            info["message_class"] = "success"
            if reload > 0:
                info["message"].append("Loaded fresh.")
            else:
                info["message"].append("Loading from cache. Use reload=1 to reload.")

            info["datfile"] = info["datfile_provenance"]
    # prepare some messages
    info["title"] = "FIELD_X: <em>%s</em> from <br />TABLE: <em>%s</em>" % (','.join(pfield), table)
    info["title"] = Markup(info["title"])
    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))
    info["results"] = Markup('<ul>' + ''.join('<li>%s</li>' % m for m in info["results"] if len(m) > 0) + '</ul>')

    # format the message to encode HTML characters
    info['query'] = Markup(request.args.get('query', ''))

    t = vis.jinja_env.get_template('explore.html')
    v1 = t.render(**info)
    t = vis.jinja_env.get_template('ml_kmeans.html')
    v2 = t.render(**info)
    v3 = v1[:-7] + v2 + v1[-7:] + '</html>'
    return Response(v3, mimetype='text/html')
