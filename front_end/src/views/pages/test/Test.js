import React, {Component} from 'react';
import { connect } from 'react-redux';
import {receiveSocketMessage, sendSocketMessage} from "../../../_actions";
import store from "../../../_helpers/store"
class Test extends Component {
  state = {
    socketData: "",
    socketStatus:"On"
  };
  componentDidMount() {

      // this.socket.on("responseMessage", message => {
      //     this.setState({'socketData': message.temperature})
      //
      //     console.log("responseMessage", message)
      // })
      store.dispatch(receiveSocketMessage("responseMessage", {'data':'Stop Sending', 'status':'Off'}));

  };

  handleEmit=()=>{
    if(this.state.socketStatus==="On"){
      store.dispatch(sendSocketMessage("message", {'data':'Stop Sending', 'status':'Off'}));
      this.setState({'socketStatus':"Off"})
    }
    else{
      store.dispatch(sendSocketMessage("message", {'data':'Start Sending', 'status':'On'}));
      this.setState({'socketStatus':"On"})
    }
    console.log("Emit Clicked")
  };
  render() {
    return (
        <React.Fragment>
            <div>Data: {this.state.socketData}</div>
          <div>Status: {this.state.socketStatus}</div>
          <div onClick={this.handleEmit}> Start/Stop</div>
        </React.Fragment>
    )
  }
}
connect()(Test);

export default Test