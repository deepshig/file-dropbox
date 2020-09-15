import React, { Component } from 'react'
import {
  TheContent,
  TheSidebar,
  TheFooter,
  TheHeader
} from './index'
import connect from "react-redux/lib/connect/connect";

class TheLayout extends Component {
    componentDidMount() {
        const { cookies } = this.props;
        cookies.set('token','123456789', { path: '/' , SameSite: 'None', Secure: true}); // TODO: Place this in a better place

        fetch("http://127.0.0.1:5000/auth/test", {
            method: "POST",
            crossDomain: true,
            credentials: 'include',
            headers: {
                "Content-Type":"application/json",
                "Accept":"application/json",
            },
            body: JSON.stringify({
                UID: 1,
            })
            }).then(response=>console.log(response.cookies))
            .then(data=>console.log({data}))
            // .then(function (data){
            //         console.log(data);
            //         cookies.save('x-access-token', data['session_id']);
            //         this.setState({message: data.Message, cookie :data['x-access-token']})
            //     }.bind(this)
            // )

    }


    render()
    {
        return (
            <div className="c-app c-default-layout">
                <TheSidebar/>
                <div className="c-wrapper">
                    <TheHeader/>
                    <div className="c-body">
                        <TheContent/>
                    </div>
                    <TheFooter/>
                </div>
            </div>
        )
    }
}
const mapStateToProps = (state, ownProps) => {
    return({
        state: state,
        cookies: ownProps.cookies,
    });
};
export const Layout = connect(
    mapStateToProps,
    null
)(TheLayout);
export default TheLayout
