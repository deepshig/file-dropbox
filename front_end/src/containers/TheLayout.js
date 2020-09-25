import React, { Component } from 'react';
import store from "../_helpers/store";
import {
  TheContent,
  TheSidebar,
  TheFooter,
  TheHeader
} from './index'
import connect from "react-redux/lib/connect/connect";
import io from "socket.io-client";

class TheLayout extends Component {
    constructor(props) {
        super(props);
        this.state = {
            socketData: "",
            socketStatus:"On",
            token: ''
        };
    }
    componentWillUnmount() {
        this.socket.close()
        console.log("component unmounted")
    }
    componentDidMount() {
        var sensorEndpoint = "http://127.0.0.1:4000"
        this.socket = io.connect(sensorEndpoint, {
            reconnection: true,
            extraHeaders: {
                Authorization: 'Bearer ' + store.getState().authentication.token
            }
            // transports: ['websocket']
        });
        console.log("component mounted")
        this.socket.on("responseMessage", message => {
            this.setState({'socketData': message.temperature})

            console.log("responseMessage", message)
        })

    }
    handleEmit=()=>{
        if(this.state.socketStatus==="On"){
            this.socket.emit("message", {'data':'Stop Sending', 'status':'Off'})
            this.setState({'socketStatus':"Off"})
        }
        else{
            this.socket.emit("message", {'data':'Start Sending', 'status':'On'})
            this.setState({'socketStatus':"On"})
        }
        console.log("Emit Clicked")
        console.log('Authorisation ' + store.getState().authentication.token)
    }


    render()
    {
        return (

            <div className="c-app c-default-layout">
                <TheSidebar/>
                <div className="c-wrapper">
                    <TheHeader/>
                    <div className="c-body">
                        <div onClick={this.handleEmit}> Start/Stop</div>

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
