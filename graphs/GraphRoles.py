membres=["@everyone"]
    roles=[""]
    ids=["@everyone"]
    count=[curseur.execute("SELECT SUM(Count) AS Total FROM {0}{1}".format(moisDB,anneeDB)).fetchone()["Total"]]
    colors=["white"]
    members=requests.get("https://discord.com/api/v9/guilds/{0}/members?limit=1000".format(guild),headers={"Authorization":"Bot Njk5NzI4NjA2NDkzOTMzNjUw.XpYnDA.ScdeM2sFekTRHY5hubkwg0HWDPU"})
    if members.status_code==200:
        members=members.json()
    table=getTableRoles(curseur,members,moisDB+anneeDB)
    for i in table:
        membres.append(roles_name[i])
        roles.append("@everyone")
        count.append(table[i])
        ids.append(roles_name[i])
        if roles_color[i]!=0:
            try:
                r,g,b=tuple(int(hex(roles_color[i])[2:][j:j+2], base=16) for j in (0, 2, 4))
                colors.append("rgb({0},{1},{2})".format(r,g,b))
            except:
                colors.append("rgb(110,200,250)")
        else:
            colors.append("rgb(110,200,250)")
    for i in members:
        num=0
        mess=curseur.execute("SELECT * FROM {0}{1} WHERE ID={2}".format(moisDB,anneeDB,i["user"]["id"])).fetchone()
        if mess!=None:
            for j in i["roles"]:
                ids.append(i["user"]["username"]+str(num))
                membres.append(i["user"]["username"])
                roles.append(roles_name[j])
                count.append(mess["Count"])
                num+=1
                if roles_color[j]!=0:
                    try:
                        r,g,b=tuple(int(hex(roles_color[j])[2:][h:h+2], base=16) for h in (0, 2, 4))
                        colors.append("rgb({0},{1},{2})".format(r,g,b))
                    except:
                        colors.append("rgb(110,200,250)")
                else:
                    colors.append("rgb(110,200,250)")

    data = dict(membres=membres,roles=roles,count=count)
    fig2 =go.Figure(go.Sunburst(
        labels=membres, parents=roles, values=count, ids=ids, marker_colors=colors
    ))
    fig2.update_yaxes(automargin=True)
    fig2.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        paper_bgcolor="rgb(47,64,120)",
        font_family="Roboto",
    )
    div2=plot(fig2,output_type='div')